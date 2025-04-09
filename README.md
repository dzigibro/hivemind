# hivemind


 Simple Linux/Windows log monitoring agent and alert server. 
 Consists of a minimal TCP server and a client agent that scans system logs for suspicious patterns and sends alerts in real-time.

---

###Features

- Works on **Linux** and **Windows**
- Scans:
  - `/var/log/` recursively on Linux
  - Event Logs on Windows (`Security`, `System`, `Application`)
- Matches for common suspicious keywords like `sudo`, `failed`, `login`, `cmd.exe`, `powershell`
- Sends alerts over TCP to central `hivemind` server
- Saves alerts to `hivemind_alerts.log` with timestamps

---

###Usage

###Start the server:
```bash
python3 hivemind_server.py
