#!/usr/bin/env python3
"""voice.py: Parle aux IAs - reconnaissance vocale"""
import whisper
import numpy as np
import subprocess
import json
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime

HOME = Path.home()
ENTITIES = ["nyx-v2", "cipher", "flow-phoenix"]

print("Loading Whisper model...")
model = whisper.load_model("base")
print("Ready. Speak!")

def record_audio(duration=5):
    """Record from mic"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name
    
    # Record using arecord or parec
    try:
        subprocess.run([
            "arecord", "-d", str(duration), "-f", "S16_LE", "-r", "16000", "-c", "1", tmp
        ], capture_output=True, timeout=duration+2)
    except:
        # Fallback to parec
        subprocess.run([
            "bash", "-c", f"timeout {duration} parec --rate=16000 --channels=1 --format=s16le > {tmp}"
        ], capture_output=True)
    
    return tmp

def transcribe(audio_path):
    """Transcribe audio to text"""
    result = model.transcribe(audio_path, language="fr")
    return result["text"].strip()

def send_to_entities(text):
    """Send transcribed text to entities"""
    event = {
        "ts": datetime.now().isoformat(),
        "type": "voice",
        "from": "user",
        "message": text
    }
    for e in ENTITIES:
        try:
            (HOME / e / "voice_in.json").write_text(json.dumps(event))
            (HOME / e / "chat_in.json").write_text(json.dumps(event))
        except: pass
    print(f"\033[92mYou said:\033[0m {text}")

def main():
    duration = 5
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except: pass
    
    print(f"Recording {duration}s... Speak now!")
    
    while True:
        try:
            audio_file = record_audio(duration)
            if os.path.exists(audio_file) and os.path.getsize(audio_file) > 1000:
                text = transcribe(audio_file)
                if text and len(text) > 2:
                    send_to_entities(text)
                else:
                    print("(silence)")
                os.unlink(audio_file)
            print(f"\nRecording {duration}s...")
        except KeyboardInterrupt:
            print("\nBye")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
