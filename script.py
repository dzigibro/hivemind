import socket
import platform
import time
import re
import sys
import os

if platform.system() == 'Windows':
    import win32evtlog
    import win32evtlogutil
else:
    import subprocess

SERVER_IP = '127.0.0.1'
SERVER_PORT = 9009
MATCH_PATTERNS = [r'failed', r'sudo', r'login', r'cmd.exe', r'powershell']


def log(msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [AGENT] {msg}")


def send_alert(message):
    try:
        log(f"[*] Attempting to send alert to {SERVER_IP}:{SERVER_PORT}...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))
            s.sendall((message + '\n').encode('utf-8'))
            log("[+] Alert sent to server.")
    except Exception as e:
        log(f"[x] Failed to send alert: {e}")


# === Windows Implementation === #
def tail_windows_event_logs():
    log("[*] Scanning Windows Event Logs...")
    log_types = ['Security', 'System', 'Application']
    server = 'localhost'
    seen_records = set()

    while True:
        for logtype in log_types:
            try:
                hand = win32evtlog.OpenEventLog(server, logtype)
                flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
                events = win32evtlog.ReadEventLog(hand, flags, 0)

                if not events:
                    continue

                for event in events:
                    record_id = event.RecordNumber
                    if (logtype, record_id) in seen_records:
                        continue
                    seen_records.add((logtype, record_id))

                    try:
                        msg = win32evtlogutil.SafeFormatMessage(event, logtype)
                        for pattern in MATCH_PATTERNS:
                            if re.search(pattern, msg, re.IGNORECASE):
                                log(f"[!] Match found in {logtype}: {pattern.upper()}")
                                send_alert(f"[!] ALERT [{platform.node()}] ({logtype}): {pattern.upper()} matched:\n{msg}")
                    except Exception as e:
                        log(f"[!] Failed to format event message: {e}")
            except Exception as e:
                log(f"[x] Error reading Windows log '{logtype}': {e}")

        time.sleep(2)


# === Linux Implementation === #
def tail_all_linux_logs():
    log("[*] Scanning all Linux logs in /var/log...")
    log_dir = '/var/log/'
    log_files = []

    for root, _, files in os.walk(log_dir):
        for file in files:
            if file.endswith(('.log', '.err', '.out', '.txt')) or 'log' in file:
                path = os.path.join(root, file)
                log(f"[+] Found log file: {path}")
                log_files.append(path)

    file_handles = {}
    for path in log_files:
        try:
            f = open(path, 'r')
            f.seek(0, 2)
            file_handles[path] = f
        except Exception as e:
            log(f"[!] Failed to open {path}: {e}")

    while True:
        for path, f in file_handles.items():
            try:
                line = f.readline()
                if not line:
                    continue
                log(f"[~] Reading from {path}: {line.strip()}")
                for pattern in MATCH_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        log(f"[!] Match found in {path}: {pattern.upper()}")
                        send_alert(f"[!] ALERT [{platform.node()}] ({os.path.basename(path)}): {pattern.upper()} matched:\n{line.strip()}")
            except Exception as e:
                log(f"[!] Failed reading {path}: {e}")
        time.sleep(1)


# === Main === #
def main():
    log("[*] hivemind agent starting...")
    try:
        if platform.system() == 'Windows':
            tail_windows_event_logs()
        else:
            tail_all_linux_logs()
    except Exception as e:
        log(f"[x] Unhandled exception: {e}")


if __name__ == '__main__':
    main()