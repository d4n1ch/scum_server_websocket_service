# SSWSS — SCUM Server WebSocket Service

**SSWSS** (SCUM Server WebSocket Service) is a lightweight WebSocket API that allows you to **read from and write to `SCUM.DB`** (the SQLite database used by SCUM dedicated servers) in real-time.

---

It is built with:
- [Python 3.10+](https://www.python.org/)
- [aiosqlite](https://github.com/omnilib/aiosqlite) for async SQLite access
- [websockets](https://websockets.readthedocs.io/) for WebSocket communication

---

## ✨ Features

- 🔒 Token-based authentication  
- 📖 Safe read-only queries (`SELECT`)  
- ✍️ Write queries (`INSERT`, `UPDATE`, `DELETE`) with auto-commit  
- ⚡ Opens database only for the duration of query → closes ASAP  
- 🗃️ Works with **WAL mode** (`SCUM.DB-wal`) safely alongside a running SCUM server  
- ⏱️ Logs execution time for every query  

---

📖 License

MIT License — free to use, modify, and distribute.
Not affiliated with SCUM, Gamepires or Jagex.