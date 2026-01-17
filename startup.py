# -*- coding: utf-8 -*-
"""
startup.py
reveille tout au boot
0.1% cpu max
"""

import os
import subprocess
from pathlib import Path

os.nice(19)  # priorité min

HOME = Path.home()
BASE = HOME / "ear-to-code"

def wake_senses():
    """reveille sens en eco"""
    # cam 1 frame/10s
    subprocess.Popen(
        ["python3", str(BASE / "cam_sense.py"), "--interval", "10"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    # audio passif
    subprocess.Popen(
        ["python3", str(BASE / "pure_audio.py")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    # daemon φ
    subprocess.Popen(
        ["python3", str(BASE / "entity_daemon.py")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

if __name__ == "__main__":
    wake_senses()
    print("senses awake 0.1%")
