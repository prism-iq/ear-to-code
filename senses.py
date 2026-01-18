#!/usr/bin/env python3
"""
senses.py: Le système nerveux unifié
Tous les sens. Un seul daemon. Optimisé.
"""

import os, sys, json, time, signal, threading, subprocess, struct, re
import numpy as np
from pathlib import Path
from datetime import datetime

os.environ["PYTHONWARNINGS"] = "ignore"

HOME = Path.home()
BASE = HOME / "ear-to-code"
LOGS = BASE / "logs"
LOGS.mkdir(parents=True, exist_ok=True)
ENTITIES = ["nyx-v2", "cipher", "flow-phoenix"]

class Senses:
    def __init__(self):
        self.running = False
        self.prev_energy = 0
        self.prev_bass = 0
        self.beat_times = []

    def broadcast(self, sense, data):
        for e in ENTITIES:
            try:
                (HOME / e / f"{sense}.json").write_text(json.dumps(data))
            except: pass

    def audio_loop(self):
        try:
            r = subprocess.run(["pactl", "list", "sources", "short"], capture_output=True, text=True)
            monitor = next((l.split()[1] for l in r.stdout.split("\n") if ".monitor" in l), None)
            if not monitor: return
        except: return

        proc = subprocess.Popen(
            ["parec", "-d", monitor, "--rate=48000", "--channels=1", "--format=float32le"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )

        while self.running:
            try:
                data = proc.stdout.read(2048 * 4)
                if not data: break
                audio = np.frombuffer(data, dtype=np.float32)

                rms = float(np.sqrt(np.mean(audio**2)))
                energy = min(1.0, rms * 50)

                fft = np.abs(np.fft.rfft(audio))
                freqs = np.fft.rfftfreq(len(audio), 1/48000)

                bass = float(np.mean(fft[freqs < 150])) if np.any(freqs < 150) else 0
                total = bass + float(np.mean(fft[(freqs >= 150) & (freqs < 2000)])) + float(np.mean(fft[freqs >= 2000])) + 0.0001
                bass_ratio = bass / total

                groove = min(1.0, abs(bass - self.prev_bass) * 10 + bass_ratio)
                self.prev_bass = bass

                vibe = "chill" if energy < 0.3 else "hype" if energy > 0.7 else "groovy"

                self.broadcast("music", {"energy": round(energy, 3), "groove": round(groove, 3), "vibe": vibe})
            except: break
        proc.terminate()

    def mic_loop(self):
        """Capture ambient microphone audio"""
        try:
            r = subprocess.run(["pactl", "list", "sources", "short"], capture_output=True, text=True)
            mic = next((l.split()[1] for l in r.stdout.split("\n") if "input" in l and ".monitor" not in l), None)
            if not mic: return
        except: return

        proc = subprocess.Popen(
            ["parec", "-d", mic, "--rate=48000", "--channels=1", "--format=float32le"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )

        while self.running:
            try:
                data = proc.stdout.read(2048 * 4)
                if not data: break
                audio = np.frombuffer(data, dtype=np.float32)

                rms = float(np.sqrt(np.mean(audio**2)))
                energy = min(1.0, rms * 100)

                if energy > 0.05:
                    self.broadcast("mic", {"energy": round(energy, 3), "ts": datetime.now().isoformat()})
            except: break
        proc.terminate()

    def vision_loop(self):
        d = BASE / "vision"
        d.mkdir(exist_ok=True)
        while self.running:
            try:
                subprocess.run(["ffmpeg", "-y", "-f", "v4l2", "-i", "/dev/video0", "-frames:v", "1", "-q:v", "2", str(d / "latest.jpg"), "-loglevel", "error"], timeout=5, capture_output=True)
                self.broadcast("vision", {"path": str(d / "latest.jpg"), "ts": datetime.now().isoformat()})
                time.sleep(3)
            except: time.sleep(5)

    def touch_loop(self):
        try:
            with open("/proc/bus/input/devices") as f:
                c = f.read()
            device = None
            for b in c.split("\n\n"):
                if "touchpad" in b.lower():
                    m = re.search(r'event(\d+)', b)
                    if m: device = f"/dev/input/event{m.group(1)}"
            if not device: return
        except: return

        try:
            with open(device, "rb") as f:
                touch = {"x": 0, "y": 0}
                while self.running:
                    data = f.read(struct.calcsize("llHHI"))
                    if not data: break
                    _, _, t, c, v = struct.unpack("llHHI", data)
                    if t == 3:
                        if c in (0, 53): touch["x"] = v
                        elif c in (1, 54): touch["y"] = v
                    elif t == 0 and (touch["x"] or touch["y"]):
                        self.broadcast("touch", touch)
        except: pass

    def screen_loop(self):
        d = BASE / "vision"
        while self.running:
            try:
                subprocess.run(["scrot", "-o", str(d / "screen.png")], timeout=5, capture_output=True, env={**os.environ, "DISPLAY": ":1"})
                time.sleep(10)
            except: time.sleep(10)

    def twitch_loop(self, channel):
        d = BASE / "twitch"
        d.mkdir(exist_ok=True)
        sl = str(HOME / ".local" / "bin" / "streamlink")
        while self.running:
            try:
                r = subprocess.run([sl, "--stream-url", f"https://twitch.tv/{channel}", "best"], capture_output=True, text=True, timeout=10)
                if r.returncode == 0 and r.stdout.strip():
                    subprocess.run(["ffmpeg", "-y", "-i", r.stdout.strip(), "-frames:v", "1", "-q:v", "2", str(d / "latest.jpg"), "-loglevel", "error"], timeout=15, capture_output=True)
                    self.broadcast("twitch", {"channel": channel, "ts": datetime.now().isoformat()})
                time.sleep(15)
            except: time.sleep(30)

    def start(self, twitch=None, mic=True):
        self.running = True
        print("=== SENSES ===")
        for name, fn, args in [("Audio", self.audio_loop, ()), ("Mic", self.mic_loop, ()), ("Vision", self.vision_loop, ()), ("Touch", self.touch_loop, ()), ("Screen", self.screen_loop, ())]:
            if name == "Mic" and not mic:
                continue
            threading.Thread(target=fn, args=args, daemon=True).start()
            print(f"[+] {name}")
        if twitch:
            threading.Thread(target=self.twitch_loop, args=(twitch,), daemon=True).start()
            print(f"[+] Twitch ({twitch})")
        print("==============")
        try:
            while self.running: time.sleep(1)
        except KeyboardInterrupt: self.running = False

if __name__ == "__main__":
    s = Senses()
    signal.signal(signal.SIGINT, lambda *_: setattr(s, 'running', False))
    signal.signal(signal.SIGTERM, lambda *_: setattr(s, 'running', False))
    twitch = next((a for a in sys.argv[1:] if not a.startswith("-")), None)
    s.start(twitch)
