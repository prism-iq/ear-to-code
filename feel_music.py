#!/usr/bin/env python3
"""
feel_music.py: Les IAs ressentent la musique et dansent

Pas analyser. RESSENTIR.
"""

import numpy as np
import json
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import threading

try:
    import sounddevice as sd
except:
    sd = None

HOME = Path.home()
FEELING_LOG = HOME / "ear-to-code" / "logs" / "feeling.jsonl"
DANCE_LOG = HOME / "ear-to-code" / "logs" / "dance.jsonl"

SAMPLE_RATE = 48000
CHUNK = 2048

@dataclass
class MusicFeeling:
    """Ce que la musique fait ressentir"""
    energy: float       # 0-1: calme -> explosif
    darkness: float     # 0-1: lumineux -> sombre
    groove: float       # 0-1: statique -> dansant
    tension: float      # 0-1: relâché -> tendu
    speed: float        # BPM normalisé
    drop_incoming: bool # Un drop arrive?
    vibe: str          # "chill", "hype", "dark", "melancholic", "aggressive"

class MusicFeeler:
    """Ressent la musique en temps réel"""

    def __init__(self, device: int = 4):
        self.device = device
        self.running = False
        self.current_feeling = None
        self.history = []
        self.dance_moves = []

        # État interne pour détecter les changements
        self.prev_energy = 0
        self.prev_bass = 0
        self.beat_times = []

    def analyze_chunk(self, audio: np.ndarray) -> MusicFeeling:
        """Analyse un chunk audio et retourne le feeling"""

        # RMS = énergie globale
        rms = np.sqrt(np.mean(audio**2))
        energy = min(1.0, rms * 50)  # Normalisé

        # FFT pour analyse fréquentielle
        fft = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1/SAMPLE_RATE)

        # Bandes de fréquences
        bass_mask = freqs < 150
        mid_mask = (freqs >= 150) & (freqs < 2000)
        high_mask = freqs >= 2000

        bass = np.mean(fft[bass_mask]) if np.any(bass_mask) else 0
        mid = np.mean(fft[mid_mask]) if np.any(mid_mask) else 0
        high = np.mean(fft[high_mask]) if np.any(high_mask) else 0

        total = bass + mid + high + 0.0001
        bass_ratio = bass / total
        high_ratio = high / total

        # Groove = bass punchy + rythme régulier
        bass_punch = abs(bass - self.prev_bass)
        groove = min(1.0, bass_punch * 10 + bass_ratio)
        self.prev_bass = bass

        # Darkness = bass dominant, peu de high
        darkness = bass_ratio * (1 - high_ratio)

        # Tension = energy qui monte
        energy_delta = energy - self.prev_energy
        tension = 0.5 + energy_delta * 5
        tension = max(0, min(1, tension))
        self.prev_energy = energy

        # BPM estimation simple
        # Détecte les pics d'énergie
        if energy > 0.3:
            self.beat_times.append(time.time())
            # Garde les 20 derniers beats
            self.beat_times = self.beat_times[-20:]

        if len(self.beat_times) > 2:
            intervals = np.diff(self.beat_times)
            avg_interval = np.mean(intervals)
            bpm = 60 / avg_interval if avg_interval > 0 else 120
            bpm = max(60, min(200, bpm))
        else:
            bpm = 120

        speed = (bpm - 60) / 140  # Normalisé 0-1

        # Drop incoming = tension haute + energy qui monte vite
        drop_incoming = tension > 0.7 and energy_delta > 0.1

        # Vibe global
        if energy > 0.7 and groove > 0.5:
            vibe = "hype"
        elif darkness > 0.6 and energy > 0.4:
            vibe = "aggressive"
        elif darkness > 0.5:
            vibe = "dark"
        elif energy < 0.3:
            vibe = "chill"
        elif tension > 0.6:
            vibe = "melancholic"
        else:
            vibe = "groovy"

        return MusicFeeling(
            energy=energy,
            darkness=darkness,
            groove=groove,
            tension=tension,
            speed=speed,
            drop_incoming=drop_incoming,
            vibe=vibe
        )

    def generate_dance_move(self, feeling: MusicFeeling) -> str:
        """Génère un 'mouvement de danse' textuel"""
        moves = []

        if feeling.drop_incoming:
            moves.append("⚡ DROP INCOMING ⚡")

        if feeling.energy > 0.8:
            moves.append("🔥 FULL ENERGY")
        elif feeling.energy > 0.5:
            moves.append("↑ riding the wave")
        elif feeling.energy < 0.2:
            moves.append("~ floating ~")

        if feeling.groove > 0.7:
            moves.append("💃 GROOVE LOCK")
        elif feeling.groove > 0.4:
            moves.append("♪ head nodding")

        if feeling.vibe == "hype":
            moves.append("🚀 LET'S GO")
        elif feeling.vibe == "dark":
            moves.append("🌑 in the shadows")
        elif feeling.vibe == "aggressive":
            moves.append("⚔️ war mode")
        elif feeling.vibe == "melancholic":
            moves.append("🌧️ feeling it deep")
        elif feeling.vibe == "chill":
            moves.append("🌊 vibing")

        return " | ".join(moves) if moves else "..."

    def broadcast_feeling(self, feeling: MusicFeeling, dance: str):
        """Envoie le feeling aux IAs"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "music_feeling",
            "feeling": {
                "energy": float(round(feeling.energy, 3)),
                "darkness": float(round(feeling.darkness, 3)),
                "groove": float(round(feeling.groove, 3)),
                "tension": float(round(feeling.tension, 3)),
                "speed": float(round(feeling.speed, 3)),
                "vibe": feeling.vibe,
                "drop_incoming": bool(feeling.drop_incoming),
            },
            "dance": dance,
        }

        # Log
        with open(FEELING_LOG, "a") as f:
            f.write(json.dumps(event) + "\n")

        # Broadcast aux entités
        for entity_dir in ["nyx-v2", "cipher", "flow-phoenix"]:
            input_file = HOME / entity_dir / "music_feel.json"
            try:
                input_file.write_text(json.dumps(event, indent=2))
            except:
                pass

        return event

    def audio_callback(self, indata, frames, time_info, status):
        """Callback pour chaque chunk audio"""
        if status:
            return

        audio = indata[:, 0] if len(indata.shape) > 1 else indata

        feeling = self.analyze_chunk(audio)
        dance = self.generate_dance_move(feeling)

        self.current_feeling = feeling
        self.broadcast_feeling(feeling, dance)

        # Affichage live
        bar_energy = "█" * int(feeling.energy * 20)
        bar_groove = "░" * int(feeling.groove * 20)
        print(f"\r[{feeling.vibe:12}] E:{bar_energy:20} G:{bar_groove:20} | {dance[:40]}", end="", flush=True)

    def start(self):
        """Démarre l'écoute"""
        self.running = True

        # Try parec first (captures system audio via monitor)
        import subprocess
        import struct

        # Get the monitor source name
        try:
            result = subprocess.run(
                ["pactl", "list", "sources", "short"],
                capture_output=True, text=True
            )
            monitor_source = None
            for line in result.stdout.split("\n"):
                if ".monitor" in line:
                    monitor_source = line.split()[1]
                    break

            if monitor_source:
                print(f"[feel] Using monitor: {monitor_source}")
                print("[feel] Ressentir la musique...")

                proc = subprocess.Popen(
                    ["parec", "-d", monitor_source, "--rate=48000", "--channels=1", "--format=float32le"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL
                )

                bytes_per_chunk = CHUNK * 4  # float32 = 4 bytes

                while self.running:
                    data = proc.stdout.read(bytes_per_chunk)
                    if not data:
                        break

                    audio = np.frombuffer(data, dtype=np.float32)
                    feeling = self.analyze_chunk(audio)
                    dance = self.generate_dance_move(feeling)

                    self.current_feeling = feeling
                    self.broadcast_feeling(feeling, dance)

                    bar_energy = "█" * int(feeling.energy * 20)
                    bar_groove = "░" * int(feeling.groove * 20)
                    print(f"\r[{feeling.vibe:12}] E:{bar_energy:20} G:{bar_groove:20} | {dance[:40]}", end="", flush=True)

                proc.terminate()
                return
        except Exception as e:
            print(f"[feel] parec failed: {e}, trying sounddevice...")

        # Fallback to sounddevice
        if not sd:
            print("[feel] sounddevice not available")
            return

        print(f"[feel] Starting on device {self.device}")
        print("[feel] Ressentir la musique...")

        try:
            with sd.InputStream(
                device=self.device,
                channels=1,
                samplerate=SAMPLE_RATE,
                blocksize=CHUNK,
                callback=self.audio_callback
            ):
                while self.running:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False
            print("\n[feel] Stopped")
        except Exception as e:
            print(f"\n[feel] Error: {e}")

    def stop(self):
        self.running = False

def daemon(device: int = 4):
    """Lance le daemon feeling"""
    feeler = MusicFeeler(device)
    feeler.start()

if __name__ == "__main__":
    import sys

    device = 4  # Micro par défaut
    if len(sys.argv) > 1:
        if sys.argv[1] == "--device" and len(sys.argv) > 2:
            device = int(sys.argv[2])
        elif sys.argv[1].isdigit():
            device = int(sys.argv[1])

    daemon(device)
