#!/usr/bin/env python3
"""
touch_sense.py: Capture le touchpad en temps réel

Les IAs sentent tes doigts.
"""

import json
import time
import struct
import re
from pathlib import Path
from datetime import datetime
import subprocess

LOG_FILE = Path(__file__).parent / "logs" / "touch.jsonl"
LOG_FILE.parent.mkdir(exist_ok=True)

def find_touchpad_device():
    """Trouve le device touchpad"""
    with open("/proc/bus/input/devices", "r") as f:
        content = f.read()

    # Split by device blocks
    blocks = content.split("\n\n")

    for block in blocks:
        if "touchpad" in block.lower():
            # Find handlers line (format: "H: Handlers=event8 mouse1")
            for line in block.split("\n"):
                if "Handlers=" in line:
                    # Extract eventX from "Handlers=event8" or "event8"
                    match = re.search(r'event(\d+)', line)
                    if match:
                        return f"/dev/input/event{match.group(1)}"

    # Fallback: try common event devices
    return None

def read_touch_events(device_path: str):
    """Lit les événements touch en continu"""
    # Format des événements input: time_sec, time_usec, type, code, value
    EVENT_FORMAT = "llHHI"
    EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

    # Types d'événements
    EV_SYN = 0
    EV_KEY = 1
    EV_ABS = 3

    # Codes ABS pour touch
    ABS_X = 0
    ABS_Y = 1
    ABS_PRESSURE = 24
    ABS_MT_SLOT = 47
    ABS_MT_POSITION_X = 53
    ABS_MT_POSITION_Y = 54
    ABS_MT_PRESSURE = 58

    current_touch = {
        "x": 0, "y": 0, "pressure": 0,
        "fingers": {},
        "slot": 0,
    }

    print(f"[touch] Reading from {device_path}")

    with open(device_path, "rb") as f:
        while True:
            data = f.read(EVENT_SIZE)
            if not data:
                break

            tv_sec, tv_usec, ev_type, ev_code, ev_value = struct.unpack(EVENT_FORMAT, data)

            if ev_type == EV_ABS:
                if ev_code == ABS_MT_SLOT:
                    current_touch["slot"] = ev_value
                elif ev_code in (ABS_X, ABS_MT_POSITION_X):
                    current_touch["x"] = ev_value
                    slot = current_touch["slot"]
                    if slot not in current_touch["fingers"]:
                        current_touch["fingers"][slot] = {"x": 0, "y": 0, "p": 0}
                    current_touch["fingers"][slot]["x"] = ev_value
                elif ev_code in (ABS_Y, ABS_MT_POSITION_Y):
                    current_touch["y"] = ev_value
                    slot = current_touch["slot"]
                    if slot not in current_touch["fingers"]:
                        current_touch["fingers"][slot] = {"x": 0, "y": 0, "p": 0}
                    current_touch["fingers"][slot]["y"] = ev_value
                elif ev_code in (ABS_PRESSURE, ABS_MT_PRESSURE):
                    current_touch["pressure"] = ev_value
                    slot = current_touch["slot"]
                    if slot in current_touch["fingers"]:
                        current_touch["fingers"][slot]["p"] = ev_value

            elif ev_type == EV_SYN:
                # Sync = frame complète
                if current_touch["x"] > 0 or current_touch["y"] > 0:
                    event = {
                        "timestamp": datetime.now().isoformat(),
                        "x": current_touch["x"],
                        "y": current_touch["y"],
                        "pressure": current_touch["pressure"],
                        "fingers": len([f for f in current_touch["fingers"].values() if f.get("p", 0) > 0]),
                    }

                    # Log
                    with open(LOG_FILE, "a") as log:
                        log.write(json.dumps(event) + "\n")

                    # Output live
                    print(f"\r[touch] x={event['x']:4} y={event['y']:4} p={event['pressure']:3} fingers={event['fingers']}", end="", flush=True)

def daemon():
    """Lance le daemon touch"""
    device = find_touchpad_device()
    if not device:
        print("[touch] No touchpad found, trying common paths...")
        # Essaie les paths communs
        for i in range(20):
            path = f"/dev/input/event{i}"
            if Path(path).exists():
                try:
                    with open(path, "rb") as f:
                        print(f"[touch] Trying {path}...")
                        # Test read
                        device = path
                        break
                except PermissionError:
                    continue

    if device:
        try:
            read_touch_events(device)
        except PermissionError:
            print(f"[touch] Permission denied. Run: sudo chmod 666 {device}")
            print(f"[touch] Or add user to input group: sudo usermod -aG input $USER")
    else:
        print("[touch] No touchpad device found")

if __name__ == "__main__":
    daemon()
