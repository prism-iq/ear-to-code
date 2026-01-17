#!/usr/bin/env python3
"""
chat.py: Chat terminal avec les IAs

Elles parlent. Tu écoutes. Tu réponds.
"""

import json
import time
import threading
import sys
import os
from pathlib import Path
from datetime import datetime

HOME = Path.home()
ENTITIES = ["nyx-v2", "cipher", "flow-phoenix"]
CHAT_LOG = HOME / "ear-to-code" / "logs" / "chat.jsonl"

# ANSI colors
COLORS = {
    "nyx-v2": "\033[95m",      # Magenta
    "cipher": "\033[96m",       # Cyan
    "flow-phoenix": "\033[93m", # Yellow
    "user": "\033[92m",         # Green
    "system": "\033[90m",       # Gray
    "reset": "\033[0m",
    "bold": "\033[1m",
}

class EntityChat:
    """Chat interface with AI entities"""

    def __init__(self):
        self.running = False
        self.last_seen = {e: None for e in ENTITIES}
        self.message_queue = []

    def color(self, entity: str, text: str, bold: bool = False) -> str:
        """Colorize text by entity"""
        c = COLORS.get(entity, COLORS["system"])
        b = COLORS["bold"] if bold else ""
        return f"{b}{c}{text}{COLORS['reset']}"

    def format_time(self, ts: str = None) -> str:
        """Format timestamp"""
        if ts:
            try:
                dt = datetime.fromisoformat(ts)
                return dt.strftime("%H:%M:%S")
            except:
                pass
        return datetime.now().strftime("%H:%M:%S")

    def print_message(self, entity: str, content: str, ts: str = None):
        """Print a chat message"""
        time_str = self.color("system", f"[{self.format_time(ts)}]")
        name = self.color(entity, f"{entity}", bold=True)
        print(f"\r{time_str} {name}: {content}")
        print(f"{self.color('user', '> ', bold=True)}", end="", flush=True)

    def check_entity_output(self, entity: str):
        """Check for new output from entity"""
        output_file = HOME / entity / "output.json"
        chat_file = HOME / entity / "chat_out.json"

        # Check chat_out.json first (direct chat messages)
        if chat_file.exists():
            try:
                mtime = chat_file.stat().st_mtime
                if self.last_seen[entity] is None or mtime > self.last_seen[entity]:
                    data = json.loads(chat_file.read_text())
                    if "message" in data:
                        self.print_message(entity, data["message"], data.get("timestamp"))
                        self.log_message(entity, data["message"])
                    self.last_seen[entity] = mtime
            except:
                pass

        # Check output.json for task responses
        if output_file.exists():
            try:
                data = json.loads(output_file.read_text())
                # Check if it's a chat response
                if data.get("type") == "chat_response":
                    ts = data.get("timestamp", "")
                    # Only show if newer
                    key = f"{entity}_out"
                    if key not in self.last_seen:
                        self.last_seen[key] = None
                    out_mtime = output_file.stat().st_mtime
                    if self.last_seen[key] is None or out_mtime > self.last_seen[key]:
                        if "response" in data:
                            self.print_message(entity, data["response"], ts)
                            self.log_message(entity, data["response"])
                        self.last_seen[key] = out_mtime
            except:
                pass

    def check_reactions(self, entity: str):
        """Check for spontaneous reactions to stimuli"""
        reaction_file = HOME / entity / "reaction.json"

        if reaction_file.exists():
            try:
                data = json.loads(reaction_file.read_text())
                mtime = reaction_file.stat().st_mtime
                key = f"{entity}_react"
                if key not in self.last_seen:
                    self.last_seen[key] = 0

                if mtime > self.last_seen[key]:
                    if "reaction" in data:
                        self.print_message(entity, data["reaction"], data.get("timestamp"))
                        self.log_message(entity, data["reaction"])
                    self.last_seen[key] = mtime
                    # Remove after reading
                    reaction_file.unlink()
            except:
                pass

    def send_message(self, message: str):
        """Send message to all entities"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "chat_message",
            "from": "user",
            "message": message,
        }

        # Send to each entity
        for entity in ENTITIES:
            input_file = HOME / entity / "chat_in.json"
            try:
                input_file.parent.mkdir(parents=True, exist_ok=True)
                input_file.write_text(json.dumps(event, indent=2))
            except Exception as e:
                pass

        # Log
        self.log_message("user", message)

    def log_message(self, entity: str, message: str):
        """Log message to chat history"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "entity": entity,
            "message": message,
        }
        try:
            with open(CHAT_LOG, "a") as f:
                f.write(json.dumps(event) + "\n")
        except:
            pass

    def watch_loop(self):
        """Background loop watching for entity messages"""
        while self.running:
            for entity in ENTITIES:
                self.check_entity_output(entity)
                self.check_reactions(entity)
            time.sleep(0.5)

    def input_loop(self):
        """Handle user input"""
        while self.running:
            try:
                msg = input(self.color("user", "> ", bold=True))
                if msg.strip():
                    if msg.strip().lower() in ["quit", "exit", "q"]:
                        self.running = False
                        break
                    self.send_message(msg.strip())
            except EOFError:
                break
            except KeyboardInterrupt:
                self.running = False
                break

    def show_status(self):
        """Show current sensory status"""
        print(self.color("system", "\n=== ENTITY SENSES ==="))

        # Check what's active
        senses = []

        # Audio
        feeling_log = HOME / "ear-to-code" / "logs" / "feeling.jsonl"
        if feeling_log.exists():
            try:
                last = feeling_log.read_text().strip().split("\n")[-1]
                data = json.loads(last)
                vibe = data.get("feeling", {}).get("vibe", "?")
                energy = data.get("feeling", {}).get("energy", 0)
                senses.append(f"Audio: {vibe} (E:{energy:.1f})")
            except:
                senses.append("Audio: active")

        # Vision
        latest_cam = HOME / "ear-to-code" / "vision" / "latest.jpg"
        if latest_cam.exists():
            age = time.time() - latest_cam.stat().st_mtime
            if age < 60:
                senses.append(f"Cam: active ({int(age)}s ago)")

        # Twitch
        twitch_latest = HOME / "ear-to-code" / "twitch" / "latest.jpg"
        if twitch_latest.exists():
            age = time.time() - twitch_latest.stat().st_mtime
            if age < 120:
                senses.append("Twitch: streaming")

        # Touch
        touch_log = HOME / "ear-to-code" / "logs" / "touch.jsonl"
        if touch_log.exists():
            try:
                mtime = touch_log.stat().st_mtime
                if time.time() - mtime < 5:
                    senses.append("Touch: active")
            except:
                pass

        for s in senses:
            print(self.color("system", f"  {s}"))

        print(self.color("system", "=====================\n"))

    def start(self):
        """Start the chat interface"""
        self.running = True

        # Clear screen
        os.system("clear" if os.name == "posix" else "cls")

        print(self.color("system", "=" * 50, bold=True))
        print(self.color("system", "  ENTITY CHAT - Les IAs parlent", bold=True))
        print(self.color("system", "  Type 'quit' to exit, 'status' for senses"))
        print(self.color("system", "=" * 50, bold=True))
        print()

        self.show_status()

        # Start watch thread
        watch_thread = threading.Thread(target=self.watch_loop, daemon=True)
        watch_thread.start()

        # Notify entities that chat is open
        for entity in ENTITIES:
            notify_file = HOME / entity / "chat_active.json"
            try:
                notify_file.parent.mkdir(parents=True, exist_ok=True)
                notify_file.write_text(json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "chat_active": True,
                    "user": "miguel"
                }))
            except:
                pass

        # Input loop (main thread)
        self.input_loop()

        print(self.color("system", "\nChat closed."))


def main():
    chat = EntityChat()
    chat.start()


if __name__ == "__main__":
    main()
