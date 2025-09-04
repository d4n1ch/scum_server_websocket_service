# -*- coding: utf-8 -*-
import datetime
import os
import json
import asyncio
import aiosqlite
import traceback
import websockets
from logger import log

section = 'main'

async def authenticate(token: str):
    from settings import auth_token
    if token == auth_token:
        return True
    else:
        return False

async def execute_safe_readonly_query(db_path: str, query: str):
    try:
        begin_at = datetime.datetime.now()
        if not os.path.exists(db_path):
            return {"error": "Database not found."}

        uri = f"file:{db_path}?mode=ro"
        async with aiosqlite.connect(uri, uri=True) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA query_only = TRUE;")
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                total = datetime.datetime.now() - begin_at
                log(section, f"Query execution took {total}")
                return [dict(row) for row in rows]
    except Exception as e:
        traceback_str = traceback.format_exc()
        log(section, f"[x] EXCEPTION: {e}")
        log(section, f"[x] EXCEPTION: {traceback_str}")
        return {"error": str(e)}

async def execute_write_query(db_path: str, query: str):
    try:
        if not os.path.exists(db_path):
            return {"error": "Database not found."}

        uri = f"file:{db_path}?mode=rw"
        async with aiosqlite.connect(uri, uri=True, timeout=10) as db:
            await db.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            await db.commit()
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute(query)
            await db.commit()
            await db.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            await db.commit()
            return {"status": "ok"}
    except Exception as e:
        traceback_str = traceback.format_exc()
        log(section, f"[x] EXCEPTION: {e}")
        log(section, f"[x] EXCEPTION: {traceback_str}")
        return {"error": str(e)}

async def handle_connection(websocket):
    client_ip, client_port = websocket.remote_address
    try:
        log(section, f"[+] New connection from {client_ip}:{client_port}")
        # First message must be auth
        auth_data = await websocket.recv()
        auth = json.loads(auth_data)
        token = auth.get("token")

        authenticated = await authenticate(token)
        if not authenticated:
            await websocket.send(json.dumps({"error": "Unauthorized"}))
            log(section, f"[*] Failed auth from {client_ip}:{client_port} with token: {token}")
            return
        from settings import scum_db
        db_path = scum_db
        await websocket.send(json.dumps({"status": "authenticated"}))
        log(section, f"[*] Successful auth from {client_ip}:{client_port}")

        while True:
            msg = await websocket.recv()
            try:
                req = json.loads(msg)
                query = req.get("query", "")
                mode_write = req.get("rw", False)
                print('mode_write', mode_write)
                begin_at = datetime.datetime.now()
                if mode_write:
                    result = await execute_write_query(db_path, query)
                else:
                    result = await execute_safe_readonly_query(db_path, query)
                log(section, f"[*] Executing query from {client_ip}:{client_port} query: {query}")
                await websocket.send(json.dumps({"result": result}))
                log(section, f"[*] Sending result to {client_ip}:{client_port}")
                total = datetime.datetime.now() - begin_at
                log(section, f"[*] Responded to {client_ip}:{client_port} in {total}")
            except Exception as err:
                traceback_str = traceback.format_exc()
                await websocket.send(json.dumps({"error": [str(err), traceback_str]}))
                log(section, f"[x] EXCEPTION: {traceback_str}")

    except websockets.exceptions.ConnectionClosed:
        pass  # client disconnected
        log(section, f"[-] Connection closed by {client_ip}:{client_port}")
    except Exception as e:
        log(section, f"[-] Exception caused by {client_ip}:{client_port}")
        traceback_str = traceback.format_exc()
        log(section, f"[x] EXCEPTION: {e}")
        log(section, f"[x] EXCEPTION: {traceback_str}")
        await websocket.send(json.dumps({"error": f"Internal server error: {e}"}))


async def start_server(wss_ip, wss_port):
    log(section,f"Starting WebSocket server at ws://{wss_ip}:{wss_port}")
    async with websockets.serve(handle_connection, wss_ip, wss_port):
        log(section, f"WebSocket server running at ws://{wss_ip}:{wss_port}")
        await asyncio.Future()

async def main():
    while True:
        try:
            from settings import wss_ip, wss_port
            await start_server(wss_ip, wss_port)
        except Exception as e:
            log(section,f"[x] EXCEPTION: WebSocket server crashed with exception: {e}")
            traceback_str = traceback.format_exc()
            log(section, f"[x] EXCEPTION: {traceback_str}")
            log(section, "[x] Restarting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log(section, "[x] Server shut down by user.")
