#!/usr/bin/env python3
"""
senses.py: Multi-sensory input capture
- Audio (microphone, system sound)
- Touch (touchpad gestures, pressure)
- System (CPU freq, voltage, temps, fan)
- Input (keyboard rhythm, mouse velocity)

Feeds everything to IAs with timestamps
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, AsyncIterator
import threading

# System metrics
import psutil

# Input devices
try:
    import evdev
    from evdev import ecodes
    EVDEV_AVAILABLE = True
except ImportError:
    EVDEV_AVAILABLE = False

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


@dataclass
class SenseEvent:
    timestamp: str
    unix_ts: float
    sense: str  # "audio", "touch", "system", "input"
    event_type: str
    data: dict

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class SystemSense:
    """Monitor system vitals: CPU, memory, temps, frequencies"""

    def __init__(self):
        self.last_cpu_freq = 0
        self.last_cpu_percent = 0

    async def read(self) -> dict:
        """Read all system metrics"""
        data = {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "cpu_freq_mhz": 0,
            "memory_percent": psutil.virtual_memory().percent,
            "temps": {},
            "fans": {},
            "battery": None,
            "load_avg": list(psutil.getloadavg()),
        }

        # CPU frequency
        freq = psutil.cpu_freq()
        if freq:
            data["cpu_freq_mhz"] = freq.current
            data["cpu_freq_min"] = freq.min
            data["cpu_freq_max"] = freq.max

        # Temperatures
        try:
            temps = psutil.sensors_temperatures()
            for name, entries in temps.items():
                data["temps"][name] = [
                    {"label": e.label, "current": e.current, "high": e.high, "critical": e.critical}
                    for e in entries
                ]
        except:
            pass

        # Fans
        try:
            fans = psutil.sensors_fans()
            for name, entries in fans.items():
                data["fans"][name] = [{"label": e.label, "current": e.current} for e in entries]
        except:
            pass

        # Battery
        try:
            bat = psutil.sensors_battery()
            if bat:
                data["battery"] = {
                    "percent": bat.percent,
                    "plugged": bat.power_plugged,
                    "secs_left": bat.secsleft if bat.secsleft > 0 else None
                }
        except:
            pass

        return data


class TouchSense:
    """Monitor touchpad events"""

    def __init__(self):
        self.device = None
        self.last_x = 0
        self.last_y = 0
        self.last_pressure = 0
        self.touches = []
        self._find_touchpad()

    def _find_touchpad(self):
        if not EVDEV_AVAILABLE:
            print("[Touch] evdev not available")
            return

        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            for d in devices:
                caps = d.capabilities()
                # Look for touchpad (has ABS_MT_POSITION_X)
                if ecodes.EV_ABS in caps:
                    abs_caps = caps[ecodes.EV_ABS]
                    abs_codes = [c[0] if isinstance(c, tuple) else c for c in abs_caps]
                    if ecodes.ABS_MT_POSITION_X in abs_codes:
                        self.device = d
                        print(f"[Touch] Found touchpad: {d.name}")
                        return
        except Exception as e:
            print(f"[Touch] Error finding touchpad: {e}")

    async def read_events(self) -> AsyncIterator[dict]:
        """Async generator of touch events"""
        if not self.device:
            return

        try:
            async for event in self.device.async_read_loop():
                if event.type == ecodes.EV_ABS:
                    if event.code == ecodes.ABS_MT_POSITION_X:
                        self.last_x = event.value
                    elif event.code == ecodes.ABS_MT_POSITION_Y:
                        self.last_y = event.value
                    elif event.code == ecodes.ABS_MT_PRESSURE:
                        self.last_pressure = event.value
                    elif event.code == ecodes.ABS_MT_TRACKING_ID:
                        if event.value >= 0:
                            # New touch
                            yield {
                                "action": "touch_start",
                                "x": self.last_x,
                                "y": self.last_y,
                                "pressure": self.last_pressure,
                                "tracking_id": event.value
                            }
                        else:
                            # Touch end
                            yield {
                                "action": "touch_end",
                                "x": self.last_x,
                                "y": self.last_y
                            }
                elif event.type == ecodes.EV_KEY:
                    # Tap events
                    if event.code == ecodes.BTN_TOUCH:
                        yield {
                            "action": "tap" if event.value else "release",
                            "x": self.last_x,
                            "y": self.last_y
                        }
        except Exception as e:
            print(f"[Touch] Read error: {e}")


class InputSense:
    """Monitor keyboard and mouse patterns"""

    def __init__(self):
        self.keyboard = None
        self.mouse = None
        self.key_times = []  # For rhythm detection
        self.mouse_positions = []  # For velocity
        self._find_devices()

    def _find_devices(self):
        if not EVDEV_AVAILABLE:
            return

        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            for d in devices:
                caps = d.capabilities()
                name_lower = d.name.lower()

                # Keyboard
                if ecodes.EV_KEY in caps and 'keyboard' in name_lower:
                    if not self.keyboard:
                        self.keyboard = d
                        print(f"[Input] Found keyboard: {d.name}")

                # Mouse
                if ecodes.EV_REL in caps:
                    if not self.mouse:
                        self.mouse = d
                        print(f"[Input] Found mouse: {d.name}")
        except Exception as e:
            print(f"[Input] Error: {e}")

    async def read_keyboard(self) -> AsyncIterator[dict]:
        """Async generator of keyboard events (rhythm, not content)"""
        if not self.keyboard:
            return

        try:
            async for event in self.keyboard.async_read_loop():
                if event.type == ecodes.EV_KEY and event.value == 1:  # Key down
                    now = time.time()
                    self.key_times.append(now)
                    # Keep last 20 keypresses
                    self.key_times = self.key_times[-20:]

                    # Calculate typing rhythm
                    if len(self.key_times) >= 2:
                        intervals = [
                            self.key_times[i] - self.key_times[i-1]
                            for i in range(1, len(self.key_times))
                        ]
                        avg_interval = sum(intervals) / len(intervals)
                        keys_per_minute = 60 / avg_interval if avg_interval > 0 else 0

                        yield {
                            "action": "keystroke",
                            "rhythm_kpm": keys_per_minute,
                            "avg_interval_ms": avg_interval * 1000,
                            "burst_count": len(self.key_times)
                        }
        except Exception as e:
            print(f"[Input] Keyboard error: {e}")

    async def read_mouse(self) -> AsyncIterator[dict]:
        """Async generator of mouse velocity events"""
        if not self.mouse:
            return

        dx, dy = 0, 0
        last_emit = time.time()

        try:
            async for event in self.mouse.async_read_loop():
                if event.type == ecodes.EV_REL:
                    if event.code == ecodes.REL_X:
                        dx += event.value
                    elif event.code == ecodes.REL_Y:
                        dy += event.value

                    now = time.time()
                    if now - last_emit > 0.1:  # Emit every 100ms
                        velocity = (dx**2 + dy**2) ** 0.5 / (now - last_emit)
                        yield {
                            "action": "mouse_move",
                            "dx": dx,
                            "dy": dy,
                            "velocity": velocity
                        }
                        dx, dy = 0, 0
                        last_emit = now
        except Exception as e:
            print(f"[Input] Mouse error: {e}")


class AllSenses:
    """Unified sensory system"""

    def __init__(self):
        self.system = SystemSense()
        self.touch = TouchSense()
        self.input = InputSense()
        self.running = False
        self.log_file = LOG_DIR / f"senses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

    def _emit(self, sense: str, event_type: str, data: dict):
        """Log and print event"""
        event = SenseEvent(
            timestamp=datetime.now().isoformat(),
            unix_ts=time.time(),
            sense=sense,
            event_type=event_type,
            data=data
        )
        with open(self.log_file, 'a') as f:
            f.write(event.to_json() + '\n')
        print(event.to_json())

    async def _system_loop(self):
        """Poll system metrics every second"""
        while self.running:
            try:
                data = await self.system.read()
                self._emit("system", "metrics", data)
            except Exception as e:
                print(f"[System] Error: {e}")
            await asyncio.sleep(1)

    async def _touch_loop(self):
        """Stream touch events"""
        async for event in self.touch.read_events():
            if not self.running:
                break
            self._emit("touch", event.get("action", "unknown"), event)

    async def _keyboard_loop(self):
        """Stream keyboard rhythm"""
        async for event in self.input.read_keyboard():
            if not self.running:
                break
            self._emit("input", "keyboard", event)

    async def _mouse_loop(self):
        """Stream mouse velocity"""
        async for event in self.input.read_mouse():
            if not self.running:
                break
            self._emit("input", "mouse", event)

    async def start(self):
        """Start all sensors"""
        self.running = True
        print(f"[SENSES] Starting all sensors...")
        print(f"[SENSES] Log: {self.log_file}")

        tasks = [
            asyncio.create_task(self._system_loop()),
        ]

        if self.touch.device:
            tasks.append(asyncio.create_task(self._touch_loop()))
        if self.input.keyboard:
            tasks.append(asyncio.create_task(self._keyboard_loop()))
        if self.input.mouse:
            tasks.append(asyncio.create_task(self._mouse_loop()))

        print(f"[SENSES] Running {len(tasks)} sensor streams")

        await asyncio.gather(*tasks)

    def stop(self):
        self.running = False


async def main():
    senses = AllSenses()
    try:
        await senses.start()
    except KeyboardInterrupt:
        print("\n[SENSES] Stopping...")
        senses.stop()


if __name__ == "__main__":
    asyncio.run(main())
