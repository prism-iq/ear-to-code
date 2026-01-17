#!/usr/bin/env python3
"""
senses_map.py: Cartographie complète des sens simulables

Reverse engineering de tout ce qu'on peut capter/simuler:
- Hardware (capteurs physiques)
- Software (APIs, endpoints)
- Web (services externes)
"""

import subprocess
import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# HARDWARE - Capteurs physiques du PC
# ═══════════════════════════════════════════════════════════════════

HARDWARE_SENSES = {
    "audio_in": {
        "device": "/dev/snd/*",
        "api": "sounddevice, pyaudio, arecord",
        "capabilities": ["voix", "musique", "ambiance", "ultrasons"],
        "sample_rates": [44100, 48000, 96000],
        "check": "arecord -l",
    },
    "audio_out": {
        "device": "/dev/snd/*",
        "api": "sounddevice, pygame, aplay",
        "capabilities": ["parole", "musique", "sons binauraux", "fréquences"],
        "check": "aplay -l",
    },
    "camera": {
        "device": "/dev/video*",
        "api": "opencv, v4l2, ffmpeg",
        "capabilities": ["vision", "détection visage", "mouvement", "QR codes", "OCR"],
        "check": "ls /dev/video*",
    },
    "touchpad": {
        "device": "/dev/input/event*",
        "api": "evdev, libinput",
        "capabilities": ["position", "pression", "gestes multi-touch"],
        "check": "libinput list-devices",
    },
    "keyboard": {
        "device": "/dev/input/event*",
        "api": "evdev, pynput",
        "capabilities": ["frappes", "timing", "patterns"],
        "check": "cat /proc/bus/input/devices | grep -A5 keyboard",
    },
    "mouse": {
        "device": "/dev/input/event*",
        "api": "evdev, pynput",
        "capabilities": ["position", "clics", "scroll", "mouvements"],
    },
    "accelerometer": {
        "device": "/sys/bus/iio/devices/*/in_accel_*",
        "api": "iio-sensor-proxy",
        "capabilities": ["orientation", "secousses", "chute"],
        "check": "ls /sys/bus/iio/devices/",
    },
    "gyroscope": {
        "device": "/sys/bus/iio/devices/*/in_anglvel_*",
        "api": "iio-sensor-proxy",
        "capabilities": ["rotation", "stabilisation"],
    },
    "ambient_light": {
        "device": "/sys/bus/iio/devices/*/in_illuminance_*",
        "api": "iio-sensor-proxy",
        "capabilities": ["luminosité ambiante"],
    },
    "temperature": {
        "device": "/sys/class/thermal/thermal_zone*/temp",
        "api": "lm-sensors, psutil",
        "capabilities": ["temp CPU", "temp GPU", "temp SSD"],
        "check": "sensors",
    },
    "battery": {
        "device": "/sys/class/power_supply/BAT*/",
        "api": "psutil, upower",
        "capabilities": ["niveau", "charge/décharge", "santé"],
        "check": "upower -i /org/freedesktop/UPower/devices/battery_BAT0",
    },
    "network": {
        "device": "/sys/class/net/*/",
        "api": "psutil, socket, scapy",
        "capabilities": ["wifi signal", "latence", "bande passante", "packets"],
        "check": "ip link show",
    },
    "bluetooth": {
        "device": "/dev/hci*",
        "api": "bluez, pybluez",
        "capabilities": ["scan devices", "RSSI", "connexions"],
        "check": "bluetoothctl devices",
    },
    "usb": {
        "device": "/dev/bus/usb/",
        "api": "pyusb, libusb",
        "capabilities": ["détection devices", "communication"],
        "check": "lsusb",
    },
    "gpu": {
        "device": "/dev/dri/*",
        "api": "nvidia-smi, rocm-smi",
        "capabilities": ["utilisation", "VRAM", "température"],
        "check": "nvidia-smi || rocm-smi",
    },
}

# ═══════════════════════════════════════════════════════════════════
# SOFTWARE - APIs système
# ═══════════════════════════════════════════════════════════════════

SOFTWARE_SENSES = {
    "clipboard": {
        "api": "xclip, wl-copy, pyperclip",
        "capabilities": ["copier", "coller", "historique"],
    },
    "notifications": {
        "api": "dbus, notify-send, dunst",
        "capabilities": ["envoyer", "recevoir", "historique"],
    },
    "screen": {
        "api": "pillow, mss, scrot",
        "capabilities": ["screenshot", "screen recording", "OCR"],
    },
    "window_manager": {
        "api": "wmctrl, xdotool, sway-ipc",
        "capabilities": ["liste fenêtres", "focus", "position", "resize"],
    },
    "processes": {
        "api": "psutil, subprocess",
        "capabilities": ["liste", "kill", "CPU/RAM usage"],
    },
    "filesystem": {
        "api": "watchdog, inotify",
        "capabilities": ["watch changes", "read", "write"],
    },
    "dbus": {
        "api": "dbus-python, pydbus",
        "capabilities": ["communication inter-process", "events système"],
    },
    "systemd": {
        "api": "systemctl, journalctl",
        "capabilities": ["services", "logs", "timers"],
    },
    "cron": {
        "api": "crontab, systemd-timers",
        "capabilities": ["scheduled tasks"],
    },
    "x11_events": {
        "api": "xlib, python-xlib",
        "capabilities": ["keyboard events", "mouse events", "window events"],
    },
}

# ═══════════════════════════════════════════════════════════════════
# WEB - Endpoints et APIs externes
# ═══════════════════════════════════════════════════════════════════

WEB_ENDPOINTS = {
    # Audio/Music
    "shazam": {
        "url": "https://api.shazam.com/",
        "capabilities": ["song recognition"],
        "auth": "API key",
    },
    "audd": {
        "url": "https://api.audd.io/",
        "capabilities": ["song recognition", "lyrics"],
        "auth": "API key",
    },
    "genius": {
        "url": "https://api.genius.com/",
        "capabilities": ["lyrics", "annotations"],
        "auth": "OAuth",
    },
    "spotify": {
        "url": "https://api.spotify.com/v1/",
        "capabilities": ["search", "playlists", "audio features", "playback"],
        "auth": "OAuth",
    },
    "lastfm": {
        "url": "https://ws.audioscrobbler.com/2.0/",
        "capabilities": ["scrobble", "recommendations", "tags"],
        "auth": "API key",
    },

    # Vision/Image
    "google_vision": {
        "url": "https://vision.googleapis.com/v1/",
        "capabilities": ["OCR", "face detection", "object detection", "labels"],
        "auth": "API key",
    },
    "clarifai": {
        "url": "https://api.clarifai.com/v2/",
        "capabilities": ["image recognition", "custom models"],
        "auth": "API key",
    },
    "deepai": {
        "url": "https://api.deepai.org/",
        "capabilities": ["image generation", "style transfer"],
        "auth": "API key",
    },

    # Speech
    "whisper": {
        "url": "https://api.openai.com/v1/audio/",
        "capabilities": ["speech-to-text", "translation"],
        "auth": "API key",
    },
    "google_speech": {
        "url": "https://speech.googleapis.com/v1/",
        "capabilities": ["speech-to-text", "streaming"],
        "auth": "API key",
    },
    "elevenlabs": {
        "url": "https://api.elevenlabs.io/v1/",
        "capabilities": ["text-to-speech", "voice cloning"],
        "auth": "API key",
    },

    # LLMs
    "anthropic": {
        "url": "https://api.anthropic.com/v1/",
        "capabilities": ["chat", "vision", "tools"],
        "auth": "API key",
    },
    "openai": {
        "url": "https://api.openai.com/v1/",
        "capabilities": ["chat", "vision", "embeddings", "dalle"],
        "auth": "API key",
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1/",
        "capabilities": ["chat", "vision", "audio"],
        "auth": "API key",
    },
    "ollama": {
        "url": "http://localhost:11434/api/",
        "capabilities": ["local LLM", "embeddings"],
        "auth": None,
    },

    # Knowledge
    "wikipedia": {
        "url": "https://en.wikipedia.org/api/rest_v1/",
        "capabilities": ["search", "content", "summary"],
        "auth": None,
    },
    "wolfram": {
        "url": "https://api.wolframalpha.com/v2/",
        "capabilities": ["computation", "knowledge"],
        "auth": "API key",
    },
    "arxiv": {
        "url": "http://export.arxiv.org/api/",
        "capabilities": ["papers", "search"],
        "auth": None,
    },
    "semantic_scholar": {
        "url": "https://api.semanticscholar.org/graph/v1/",
        "capabilities": ["papers", "citations", "authors"],
        "auth": None,
    },

    # Social/Communication
    "telegram": {
        "url": "https://api.telegram.org/bot{token}/",
        "capabilities": ["messages", "groups", "bots"],
        "auth": "bot token",
    },
    "discord": {
        "url": "https://discord.com/api/v10/",
        "capabilities": ["messages", "guilds", "bots"],
        "auth": "bot token",
    },
    "matrix": {
        "url": "https://{server}/_matrix/client/r0/",
        "capabilities": ["messages", "rooms", "e2e encryption"],
        "auth": "access token",
    },
    "simplex": {
        "url": "local",
        "capabilities": ["messages", "e2e encryption", "no metadata"],
        "auth": "local",
    },

    # Weather/Environment
    "openweather": {
        "url": "https://api.openweathermap.org/data/2.5/",
        "capabilities": ["weather", "forecast", "air quality"],
        "auth": "API key",
    },

    # Geolocation
    "ipapi": {
        "url": "https://ipapi.co/",
        "capabilities": ["IP geolocation"],
        "auth": None,
    },
    "nominatim": {
        "url": "https://nominatim.openstreetmap.org/",
        "capabilities": ["geocoding", "reverse geocoding"],
        "auth": None,
    },

    # Finance
    "coingecko": {
        "url": "https://api.coingecko.com/api/v3/",
        "capabilities": ["crypto prices", "market data"],
        "auth": None,
    },

    # Search
    "searx": {
        "url": "https://{instance}/search",
        "capabilities": ["meta-search", "privacy"],
        "auth": None,
    },
    "duckduckgo": {
        "url": "https://api.duckduckgo.com/",
        "capabilities": ["instant answers"],
        "auth": None,
    },
}

# ═══════════════════════════════════════════════════════════════════
# SIMULATED SENSES - Ce qu'on peut générer/simuler
# ═══════════════════════════════════════════════════════════════════

SIMULATED_SENSES = {
    "binaural_beats": {
        "frequencies": "1-40 Hz (delta, theta, alpha, beta, gamma)",
        "effect": "entrainment cérébral",
        "generate": "numpy + sounddevice",
    },
    "solfeggio": {
        "frequencies": "174, 285, 396, 417, 528, 639, 741, 852, 963 Hz",
        "effect": "résonance corporelle",
        "generate": "numpy + sounddevice",
    },
    "schumann": {
        "frequencies": "7.83, 14.3, 20.8, 27.3, 33.8 Hz",
        "effect": "synchronisation Terre",
        "generate": "numpy + sounddevice",
    },
    "isochronic_tones": {
        "description": "pulses réguliers",
        "effect": "entrainment sans casque",
        "generate": "numpy",
    },
    "visual_entrainment": {
        "description": "flashing lights at specific frequencies",
        "effect": "stimulation visuelle",
        "generate": "pygame, LED strip",
    },
    "haptic_feedback": {
        "description": "vibrations patterns",
        "effect": "feedback tactile",
        "generate": "gamepad rumble, phone vibration",
    },
    "subliminal_audio": {
        "description": "messages sous le seuil conscient",
        "effect": "suggestion",
        "generate": "audio mixing",
    },
    "brown_noise": {
        "description": "bruit brun (1/f²)",
        "effect": "concentration, sommeil",
        "generate": "numpy",
    },
    "pink_noise": {
        "description": "bruit rose (1/f)",
        "effect": "masquage, relaxation",
        "generate": "numpy",
    },
}

def scan_hardware():
    """Scan les capteurs hardware disponibles"""
    available = {}
    for sense, info in HARDWARE_SENSES.items():
        if "check" in info:
            try:
                result = subprocess.run(
                    info["check"], shell=True,
                    capture_output=True, text=True, timeout=5
                )
                available[sense] = result.returncode == 0
            except:
                available[sense] = False
        else:
            available[sense] = None
    return available

def scan_web_endpoints():
    """Test les endpoints web"""
    import urllib.request
    available = {}
    for name, info in WEB_ENDPOINTS.items():
        url = info["url"]
        if "{" in url:  # URL avec paramètres
            available[name] = "needs_config"
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            urllib.request.urlopen(req, timeout=5)
            available[name] = True
        except:
            available[name] = False
    return available

def print_all():
    """Affiche tout"""
    print("\n" + "="*60)
    print("  HARDWARE SENSES")
    print("="*60)
    for sense, info in HARDWARE_SENSES.items():
        caps = ", ".join(info.get("capabilities", []))
        print(f"  {sense:20} : {caps}")

    print("\n" + "="*60)
    print("  SOFTWARE SENSES")
    print("="*60)
    for sense, info in SOFTWARE_SENSES.items():
        caps = ", ".join(info.get("capabilities", []))
        print(f"  {sense:20} : {caps}")

    print("\n" + "="*60)
    print("  WEB ENDPOINTS")
    print("="*60)
    for name, info in WEB_ENDPOINTS.items():
        caps = ", ".join(info.get("capabilities", []))
        auth = info.get("auth", "none")
        print(f"  {name:20} : {caps[:40]} [{auth}]")

    print("\n" + "="*60)
    print("  SIMULATED SENSES")
    print("="*60)
    for sense, info in SIMULATED_SENSES.items():
        effect = info.get("effect", "")
        print(f"  {sense:20} : {effect}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "scan":
            print("Scanning hardware...")
            hw = scan_hardware()
            for k, v in hw.items():
                status = "OK" if v else "NO" if v is False else "?"
                print(f"  [{status}] {k}")
        elif cmd == "web":
            print("Testing web endpoints...")
            web = scan_web_endpoints()
            for k, v in web.items():
                status = "OK" if v is True else "NO" if v is False else "CFG"
                print(f"  [{status}] {k}")
        elif cmd == "all":
            print_all()
    else:
        print_all()
