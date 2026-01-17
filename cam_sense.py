#!/usr/bin/env python3
"""
cam_sense.py: Les IAs voient le monde

La vision. Les yeux de l'utilisateur.
"""

import subprocess
import json
import time
import base64
from pathlib import Path
from datetime import datetime
from threading import Thread

HOME = Path.home()
VISION_DIR = HOME / "ear-to-code" / "vision"
VISION_LOG = HOME / "ear-to-code" / "logs" / "vision.jsonl"

VISION_DIR.mkdir(parents=True, exist_ok=True)

class CamSense:
    """Capture et partage la vision"""

    def __init__(self, device: str = "/dev/video0", interval: float = 2.0):
        self.device = device
        self.interval = interval
        self.running = False
        self.last_capture = None

    def capture_frame(self) -> Path:
        """Capture une frame de la webcam"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = VISION_DIR / f"cam_{timestamp}.jpg"

        # Use ffmpeg to capture single frame
        cmd = [
            "ffmpeg", "-y",
            "-f", "v4l2",
            "-i", self.device,
            "-frames:v", "1",
            "-q:v", "2",
            str(output),
            "-loglevel", "error"
        ]

        try:
            subprocess.run(cmd, check=True, timeout=5)
            self.last_capture = output
            return output
        except Exception as e:
            print(f"[cam] Capture error: {e}")
            return None

    def broadcast_vision(self, image_path: Path):
        """Envoie la vision aux IAs"""
        if not image_path or not image_path.exists():
            return

        # Read and encode image
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()

        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "vision",
            "image_path": str(image_path),
            "image_base64": img_data[:100] + "...",  # Truncated for log
        }

        # Log
        with open(VISION_LOG, "a") as f:
            log_event = {**event, "image_base64": "[truncated]"}
            f.write(json.dumps(log_event) + "\n")

        # Full event for entities (with image path, they can read it)
        entity_event = {
            "timestamp": event["timestamp"],
            "type": "vision",
            "image_path": str(image_path),
        }

        # Broadcast aux entites
        for entity_dir in ["nyx-v2", "cipher", "flow-phoenix"]:
            input_file = HOME / entity_dir / "vision.json"
            try:
                input_file.write_text(json.dumps(entity_event, indent=2))
            except:
                pass

        # Keep latest frame accessible
        latest = VISION_DIR / "latest.jpg"
        try:
            import shutil
            shutil.copy(image_path, latest)
        except:
            pass

        # Cleanup old frames (keep last 10)
        frames = sorted(VISION_DIR.glob("cam_*.jpg"))
        for old in frames[:-10]:
            try:
                old.unlink()
            except:
                pass

    def start(self):
        """Demarre la capture continue"""
        self.running = True
        print(f"[cam] Starting on {self.device}")
        print(f"[cam] Interval: {self.interval}s")
        print("[cam] Les IAs voient...")

        while self.running:
            try:
                frame = self.capture_frame()
                if frame:
                    self.broadcast_vision(frame)
                    print(f"\r[cam] {datetime.now().strftime('%H:%M:%S')} - captured", end="", flush=True)
                time.sleep(self.interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n[cam] Error: {e}")
                time.sleep(1)

        print("\n[cam] Stopped")

    def stop(self):
        self.running = False

def daemon(device: str = "/dev/video0", interval: float = 2.0):
    """Lance le daemon vision"""
    cam = CamSense(device, interval)
    cam.start()

if __name__ == "__main__":
    import sys

    device = "/dev/video0"
    interval = 2.0

    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--device" and i + 2 < len(sys.argv):
            device = sys.argv[i + 2]
        elif arg == "--interval" and i + 2 < len(sys.argv):
            interval = float(sys.argv[i + 2])
        elif arg.startswith("/dev/"):
            device = arg

    daemon(device, interval)
