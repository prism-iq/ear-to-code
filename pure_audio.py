#!/usr/bin/env python3
"""
pure_audio.py: Audio analysis without numpy
Pure Python + Linux tools only
"""

import struct
import subprocess
import math
import json
from pathlib import Path
from datetime import datetime

HOME = Path.home()
ENTITIES = ["nyx-v2", "cipher", "flow-phoenix"]

def rms(samples: list) -> float:
    """Root mean square - pure Python"""
    if not samples:
        return 0.0
    return math.sqrt(sum(s*s for s in samples) / len(samples))

def simple_fft_power(samples: list, sample_rate: int = 48000) -> dict:
    """
    Simple frequency band power estimation without FFT.
    Uses zero-crossing rate and amplitude variance as proxies.
    """
    if len(samples) < 100:
        return {"bass": 0, "mid": 0, "high": 0}
    
    # Zero crossing rate (correlates with high frequency content)
    zero_crossings = sum(1 for i in range(1, len(samples)) if samples[i-1] * samples[i] < 0)
    zcr = zero_crossings / len(samples)
    
    # Amplitude variance (correlates with energy distribution)
    mean_amp = sum(abs(s) for s in samples) / len(samples)
    variance = sum((abs(s) - mean_amp)**2 for s in samples) / len(samples)
    
    # Rough estimation
    high = min(1.0, zcr * 10)
    bass = min(1.0, variance * 100) * (1 - high)
    mid = 1 - bass - high
    
    return {"bass": bass, "mid": max(0, mid), "high": high}

def analyze_audio(samples: list) -> dict:
    """Analyze audio chunk - pure Python"""
    energy = min(1.0, rms(samples) * 30)
    
    bands = simple_fft_power(samples)
    bass = bands["bass"]
    
    # Simplified vibe detection
    if energy > 0.6:
        vibe = "hype"
    elif energy < 0.2:
        vibe = "chill"
    elif bass > 0.5:
        vibe = "dark"
    else:
        vibe = "groovy"
    
    return {
        "energy": round(energy, 3),
        "groove": round(bass, 3),
        "vibe": vibe
    }

def broadcast(data: dict):
    """Send to entities"""
    for e in ENTITIES:
        try:
            (HOME / e / "music.json").write_text(json.dumps(data))
        except:
            pass

def capture_loop(source: str = "alsa_input.pci-0000_c1_00.6.HiFi__Mic1__source"):
    """Main capture loop using parec"""
    print(f"[pure_audio] Source: {source}")
    
    proc = subprocess.Popen(
        ["parec", "-d", source, "--rate=48000", "--channels=1", "--format=float32le"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    
    chunk_size = 2048
    
    while True:
        try:
            raw = proc.stdout.read(chunk_size * 4)  # 4 bytes per float32
            if not raw:
                break
            
            # Unpack float32 samples - pure struct
            samples = list(struct.unpack(f'{len(raw)//4}f', raw))
            
            result = analyze_audio(samples)
            broadcast(result)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[err] {e}")
            break
    
    proc.terminate()

if __name__ == "__main__":
    import sys
    source = sys.argv[1] if len(sys.argv) > 1 else "alsa_input.pci-0000_c1_00.6.HiFi__Mic1__source"
    capture_loop(source)
