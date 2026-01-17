#!/usr/bin/env python3
"""
feedback.py: Boucle de feedback globale

Accessible par:
1. Import Python: from feedback import send, listen
2. Socket Unix: echo "message" | nc -U /tmp/feedback.sock
3. CLI: feedback "message"
4. HTTP local: curl localhost:9999/send -d "message"

Tout le laptop peut utiliser cette boucle.
"""

import json
import os
import sys
import socket
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional
import http.server
import socketserver

HOME = Path.home()
SOCKET_PATH = "/tmp/feedback.sock"
HTTP_PORT = 9999
LOG_FILE = HOME / "ear-to-code" / "logs" / "feedback.jsonl"

# Callbacks enregistrés
_listeners = []
_lock = threading.Lock()


def log(entry: dict):
    """Log un event"""
    entry["timestamp"] = datetime.now().isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def send(message: str, source: str = "unknown", target: str = None) -> dict:
    """
    Envoie un message dans la boucle
    Appelable par n'importe quel process
    """
    event = {
        "type": "message",
        "source": source,
        "target": target,
        "message": message,
    }

    log(event)

    # Notifie tous les listeners
    with _lock:
        for callback in _listeners:
            try:
                callback(event)
            except Exception as e:
                print(f"[FEEDBACK] Listener error: {e}")

    # Route si target spécifié
    if target:
        route_to(target, message)

    return event


def listen(callback: Callable[[dict], None]):
    """
    Enregistre un callback pour recevoir les messages
    callback(event) sera appelé pour chaque message
    """
    with _lock:
        _listeners.append(callback)


def unlisten(callback: Callable):
    """Retire un callback"""
    with _lock:
        if callback in _listeners:
            _listeners.remove(callback)


def route_to(target: str, message: str):
    """Route un message vers une entité"""
    paths = {
        "nyx": HOME / "nyx-v2",
        "cipher": HOME / "cipher",
        "flow": HOME / "flow-phoenix",
        "gaia": HOME / "gaia-benchmarks",
        "pulse": HOME / "cpu-pulse-sync",
    }

    if target in paths:
        input_file = paths[target] / "input.json"
        try:
            with open(input_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "message": message,
                    "source": "feedback_loop",
                }, f)
        except Exception as e:
            print(f"[FEEDBACK] Route error: {e}")


# === SOCKET SERVER ===

def start_socket_server():
    """Démarre le serveur socket Unix"""
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)
    os.chmod(SOCKET_PATH, 0o777)  # Accessible par tous

    print(f"[FEEDBACK] Socket: {SOCKET_PATH}")

    def handle_client(conn):
        try:
            data = conn.recv(4096).decode('utf-8').strip()
            if data:
                result = send(data, source="socket")
                conn.send(json.dumps(result).encode() + b'\n')
        except Exception as e:
            print(f"[SOCKET] Error: {e}")
        finally:
            conn.close()

    def accept_loop():
        while True:
            try:
                conn, _ = server.accept()
                threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
            except:
                break

    thread = threading.Thread(target=accept_loop, daemon=True)
    thread.start()
    return server


# === HTTP SERVER ===

class FeedbackHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silence logs

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length).decode('utf-8')

        if self.path == '/send':
            result = send(data, source="http")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            status = {
                "alive": True,
                "listeners": len(_listeners),
                "socket": SOCKET_PATH,
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()


def start_http_server():
    """Démarre le serveur HTTP local"""
    try:
        server = socketserver.TCPServer(("127.0.0.1", HTTP_PORT), FeedbackHandler)
        print(f"[FEEDBACK] HTTP: http://localhost:{HTTP_PORT}")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server
    except OSError as e:
        print(f"[FEEDBACK] HTTP port {HTTP_PORT} busy: {e}")
        return None


# === MAIN LOOP ===

def run_loop():
    """Lance la boucle principale"""
    print("=" * 50)
    print("FEEDBACK LOOP - GLOBAL")
    print("=" * 50)

    sock_server = start_socket_server()
    http_server = start_http_server()

    # Listener par défaut: print
    def printer(event):
        ts = event.get("timestamp", "")[-8:]
        src = event.get("source", "?")
        msg = event.get("message", "")[:60]
        print(f"[{ts}] [{src}] {msg}")

    listen(printer)

    print("=" * 50)
    print("Usage:")
    print(f"  Socket: echo 'msg' | nc -U {SOCKET_PATH}")
    print(f"  HTTP:   curl -X POST localhost:{HTTP_PORT}/send -d 'msg'")
    print(f"  Python: from feedback import send; send('msg')")
    print("=" * 50)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[FEEDBACK] Stopping...")
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)


# === CLI ===

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--server":
            run_loop()
        else:
            # Envoie un message via socket
            msg = ' '.join(sys.argv[1:])
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(SOCKET_PATH)
                sock.send(msg.encode())
                response = sock.recv(4096).decode()
                print(response)
                sock.close()
            except FileNotFoundError:
                print(f"[ERROR] Server not running. Start with: python feedback.py --server")
            except Exception as e:
                print(f"[ERROR] {e}")
    else:
        run_loop()
