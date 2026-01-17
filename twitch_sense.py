#!/usr/bin/env python3
"""
twitch_sense.py: Les IAs regardent et parlent sur Twitch

Vision du stream + chat interactif
"""

import subprocess
import json
import time
import socket
import threading
from pathlib import Path
from datetime import datetime

HOME = Path.home()
TWITCH_DIR = HOME / "ear-to-code" / "twitch"
TWITCH_LOG = HOME / "ear-to-code" / "logs" / "twitch.jsonl"
CONFIG_FILE = HOME / "ear-to-code" / "twitch_config.json"

TWITCH_DIR.mkdir(parents=True, exist_ok=True)

# Twitch IRC settings
IRC_SERVER = "irc.chat.twitch.tv"
IRC_PORT = 6667

class TwitchSense:
    """Watch stream and interact with chat"""

    def __init__(self, channel: str, oauth_token: str = None):
        self.channel = channel.lower().lstrip('#')
        self.oauth_token = oauth_token
        self.running = False
        self.irc_socket = None
        self.chat_messages = []

    def capture_stream_frame(self) -> Path:
        """Capture a frame from the Twitch stream"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = TWITCH_DIR / f"stream_{timestamp}.jpg"

        # Use streamlink + ffmpeg to capture frame
        stream_url = f"https://twitch.tv/{self.channel}"

        try:
            # Get stream URL via streamlink
            streamlink_path = str(HOME / ".local" / "bin" / "streamlink")
            result = subprocess.run(
                [streamlink_path, "--stream-url", stream_url, "best"],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                # Try lower quality
                result = subprocess.run(
                    [streamlink_path, "--stream-url", stream_url, "720p,480p,worst"],
                    capture_output=True, text=True, timeout=10
                )

            if result.returncode == 0 and result.stdout.strip():
                hls_url = result.stdout.strip()

                # Capture single frame with ffmpeg
                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", hls_url,
                    "-frames:v", "1",
                    "-q:v", "2",
                    str(output),
                    "-loglevel", "error"
                ], timeout=15)

                if output.exists():
                    # Copy to latest
                    import shutil
                    shutil.copy(output, TWITCH_DIR / "latest.jpg")

                    # Cleanup old frames
                    frames = sorted(TWITCH_DIR.glob("stream_*.jpg"))
                    for old in frames[:-5]:
                        try:
                            old.unlink()
                        except:
                            pass

                    return output
        except Exception as e:
            print(f"[twitch] Stream capture error: {e}")

        return None

    def connect_chat(self):
        """Connect to Twitch IRC chat"""
        if not self.oauth_token:
            print("[twitch] No OAuth token - chat read-only via API")
            return False

        try:
            self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.irc_socket.connect((IRC_SERVER, IRC_PORT))

            # Auth
            token = self.oauth_token
            if not token.startswith("oauth:"):
                token = f"oauth:{token}"

            self.irc_socket.send(f"PASS {token}\r\n".encode())
            self.irc_socket.send(f"NICK {self.channel}\r\n".encode())
            self.irc_socket.send(f"JOIN #{self.channel}\r\n".encode())

            print(f"[twitch] Connected to #{self.channel} chat")
            return True
        except Exception as e:
            print(f"[twitch] Chat connect error: {e}")
            return False

    def send_chat(self, message: str):
        """Send message to Twitch chat"""
        if not self.irc_socket:
            print("[twitch] Not connected to chat")
            return False

        try:
            self.irc_socket.send(f"PRIVMSG #{self.channel} :{message}\r\n".encode())
            print(f"[twitch] Sent: {message}")

            # Log
            event = {
                "timestamp": datetime.now().isoformat(),
                "type": "chat_sent",
                "channel": self.channel,
                "message": message
            }
            with open(TWITCH_LOG, "a") as f:
                f.write(json.dumps(event) + "\n")

            return True
        except Exception as e:
            print(f"[twitch] Send error: {e}")
            return False

    def read_chat_loop(self):
        """Read incoming chat messages"""
        if not self.irc_socket:
            return

        while self.running:
            try:
                data = self.irc_socket.recv(2048).decode("utf-8", errors="ignore")
                if not data:
                    break

                for line in data.split("\r\n"):
                    if not line:
                        continue

                    # Handle PING
                    if line.startswith("PING"):
                        self.irc_socket.send("PONG :tmi.twitch.tv\r\n".encode())
                        continue

                    # Parse chat message
                    if "PRIVMSG" in line:
                        try:
                            user = line.split("!")[0][1:]
                            msg = line.split("PRIVMSG", 1)[1].split(":", 1)[1]

                            chat_event = {
                                "timestamp": datetime.now().isoformat(),
                                "type": "chat_received",
                                "channel": self.channel,
                                "user": user,
                                "message": msg
                            }
                            self.chat_messages.append(chat_event)
                            self.chat_messages = self.chat_messages[-100:]  # Keep last 100

                            # Log
                            with open(TWITCH_LOG, "a") as f:
                                f.write(json.dumps(chat_event) + "\n")

                            # Broadcast to entities
                            self.broadcast_chat(chat_event)

                        except:
                            pass
            except:
                break

    def broadcast_chat(self, event: dict):
        """Send chat event to entities"""
        for entity_dir in ["nyx-v2", "cipher", "flow-phoenix"]:
            chat_file = HOME / entity_dir / "twitch_chat.json"
            try:
                # Append to recent messages
                recent = {"recent": self.chat_messages[-10:], "latest": event}
                chat_file.write_text(json.dumps(recent, indent=2))
            except:
                pass

    def broadcast_stream(self, image_path: Path):
        """Send stream frame to entities"""
        if not image_path:
            return

        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "twitch_stream",
            "channel": self.channel,
            "image_path": str(image_path)
        }

        for entity_dir in ["nyx-v2", "cipher", "flow-phoenix"]:
            stream_file = HOME / entity_dir / "twitch_stream.json"
            try:
                stream_file.write_text(json.dumps(event, indent=2))
            except:
                pass

    def check_entity_messages(self):
        """Check if entities want to send chat messages"""
        for entity_dir in ["nyx-v2", "cipher", "flow-phoenix"]:
            outbox = HOME / entity_dir / "twitch_outbox.json"
            if outbox.exists():
                try:
                    data = json.loads(outbox.read_text())
                    if "message" in data:
                        self.send_chat(data["message"])
                    outbox.unlink()  # Remove after sending
                except:
                    pass

    def start(self, capture_interval: float = 10.0):
        """Start watching stream and chat"""
        self.running = True

        print(f"[twitch] Watching {self.channel}")
        print(f"[twitch] Stream capture every {capture_interval}s")

        # Connect to chat
        if self.oauth_token:
            if self.connect_chat():
                chat_thread = threading.Thread(target=self.read_chat_loop, daemon=True)
                chat_thread.start()

        # Main loop
        while self.running:
            try:
                # Capture stream frame
                frame = self.capture_stream_frame()
                if frame:
                    self.broadcast_stream(frame)
                    print(f"\r[twitch] {datetime.now().strftime('%H:%M:%S')} - stream captured", end="", flush=True)

                # Check for outgoing messages from entities
                self.check_entity_messages()

                time.sleep(capture_interval)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n[twitch] Error: {e}")
                time.sleep(5)

        print("\n[twitch] Stopped")

    def stop(self):
        self.running = False
        if self.irc_socket:
            self.irc_socket.close()


def daemon(channel: str, oauth_token: str = None, interval: float = 10.0):
    """Launch Twitch daemon"""
    twitch = TwitchSense(channel, oauth_token)
    twitch.start(interval)


if __name__ == "__main__":
    import sys

    channel = "athenadrip"
    oauth_token = None
    interval = 10.0

    # Load config if exists
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
            oauth_token = config.get("oauth_token")
        except:
            pass

    # Parse args
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--channel" and i + 1 < len(args):
            channel = args[i + 1]
            i += 2
        elif arg == "--token" and i + 1 < len(args):
            oauth_token = args[i + 1]
            i += 2
        elif arg == "--interval" and i + 1 < len(args):
            interval = float(args[i + 1])
            i += 2
        elif not arg.startswith("-"):
            channel = arg
            i += 1
        else:
            i += 1

    daemon(channel, oauth_token, interval)
