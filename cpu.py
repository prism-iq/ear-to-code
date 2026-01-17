# -*- coding: utf-8 -*-
"""
cpu.py
constantes cpu
limite 40%
"""

import os
import time

# constantes
MAX_CPU = 40  # %
SLEEP_RATIO = 0.6 / 0.4  # 60% sleep 40% work

def limit():
    """auto-limite cpu"""
    os.nice(10)  # basse priorité

def throttle(func):
    """décorateur throttle"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        sleep_time = elapsed * SLEEP_RATIO
        if sleep_time > 0:
            time.sleep(min(sleep_time, 1))
        return result
    return wrapper

if __name__ == "__main__":
    limit()
    print(f"cpu max: {MAX_CPU}%")
    print(f"nice: 10")
