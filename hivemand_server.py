import socket
import threading
import datetime
import os
from colorama import Fore, Style, init

init(autoreset=True)

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 9009
LOG_FILE = 'hivemind_alerts.log'


def verbose_log(message, level="info"):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    color = {
        "info": Fore.CYAN,
        "alert": Fore.RED + Style.BRIGHT,
        "error": Fore.YELLOW,
        "connect": Fore.GREEN,
    }.get(level, Fore.WHITE)

    print(f"{color}[{timestamp}] [HIVEMIND SERVER] {message}{Style.RESET_ALL}")


def handle_client(conn, addr):
    with conn:
        buffer = b""
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break

                buffer += data
                if b"\n" in buffer:
                    messages = buffer.split(b"\n")
                    buffer = messages.pop()

                    for msg_bytes in messages:
                        try:
                            message = msg_bytes.decode('utf-8', errors='replace').strip()
                            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            log_entry = f"[{timestamp}] [{addr[0]}] {message}"

                            verbose_log(f"[ALERT RECEIVED] {log_entry}", level="alert")

                            with open(LOG_FILE, 'a') as log:
                                log.write(log_entry + '\n')

                        except Exception as e:
                            verbose_log(f"[!] Failed to decode message from {addr}: {e}", level="error")

            except Exception as e:
                verbose_log(f"[!] Error handling client {addr}: {e}", level="error")
                break


def start_server():
    verbose_log(f"[*] hivemind server listening on {SERVER_HOST}:{SERVER_PORT}...", level="connect")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((SERVER_HOST, SERVER_PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()


if __name__ == '__main__':
    start_server()
