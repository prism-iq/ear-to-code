#!/usr/bin/env python3
"""
full_sense.py: UNIFIED SENSORY SYSTEM
Combines all inputs into one stream for AI consumption:
- Audio (music recognition, lyrics, features)
- Touch (touchpad gestures)
- System (CPU, temps, voltages, battery)
- Input (keyboard rhythm, mouse velocity)

ALL timestamped, ALL persistent, NEVER dies
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Import our modules
from ear import EarToCode, find_monitor_device, list_devices
from senses import AllSenses, SystemSense, TouchSense, InputSense

LOG_DIR = Path(__file__).parent / "logs"


class UnifiedSense:
    """The complete sensory system"""

    def __init__(self, audio_device=None):
        # Audio ear
        self.ear = EarToCode(device=audio_device)

        # Other senses
        self.system = SystemSense()
        self.touch = TouchSense()
        self.input_sense = InputSense()

        self.running = False
        self.log_file = LOG_DIR / f"unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

        # Link all outputs to unified log
        self.ear.on_event = self._on_audio_event

    def _log(self, event: dict):
        """Write to unified log"""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
        print(json.dumps(event, ensure_ascii=False))

    def _on_audio_event(self, event):
        """Forward audio events to unified log"""
        self._log({
            "timestamp": event.timestamp,
            "unix_ts": event.unix_ts,
            "sense": "audio",
            "event_type": event.event_type,
            "data": event.data
        })

    async def _system_loop(self):
        """System metrics every second"""
        while self.running:
            try:
                data = await self.system.read()
                self._log({
                    "timestamp": datetime.now().isoformat(),
                    "unix_ts": __import__('time').time(),
                    "sense": "system",
                    "event_type": "metrics",
                    "data": data
                })
            except Exception as e:
                print(f"[System Error] {e}")
            await asyncio.sleep(1)

    async def _touch_loop(self):
        """Touch events"""
        async for event in self.touch.read_events():
            if not self.running:
                break
            self._log({
                "timestamp": datetime.now().isoformat(),
                "unix_ts": __import__('time').time(),
                "sense": "touch",
                "event_type": event.get("action", "unknown"),
                "data": event
            })

    async def _keyboard_loop(self):
        """Keyboard rhythm"""
        async for event in self.input_sense.read_keyboard():
            if not self.running:
                break
            self._log({
                "timestamp": datetime.now().isoformat(),
                "unix_ts": __import__('time').time(),
                "sense": "input",
                "event_type": "keyboard",
                "data": event
            })

    async def _mouse_loop(self):
        """Mouse velocity"""
        async for event in self.input_sense.read_mouse():
            if not self.running:
                break
            self._log({
                "timestamp": datetime.now().isoformat(),
                "unix_ts": __import__('time').time(),
                "sense": "input",
                "event_type": "mouse",
                "data": event
            })

    async def start(self):
        """Start everything"""
        self.running = True

        print("=" * 60)
        print("UNIFIED SENSORY SYSTEM")
        print("=" * 60)
        print(f"Log: {self.log_file}")
        print("Senses:")
        print(f"  - Audio: {'System (pipewire)' if self.ear.device else 'Default mic'}")
        print(f"  - Touch: {'Active' if self.touch.device else 'Not found'}")
        print(f"  - Keyboard: {'Active' if self.input_sense.keyboard else 'Not found'}")
        print(f"  - Mouse: {'Active' if self.input_sense.mouse else 'Not found'}")
        print(f"  - System: Always active (CPU, temps, battery)")
        print("=" * 60)
        print("NEVER DIES - auto-reconnect on all channels")
        print("=" * 60)

        tasks = [
            asyncio.create_task(self.ear.start()),
            asyncio.create_task(self._system_loop()),
        ]

        if self.touch.device:
            tasks.append(asyncio.create_task(self._touch_loop()))
        if self.input_sense.keyboard:
            tasks.append(asyncio.create_task(self._keyboard_loop()))
        if self.input_sense.mouse:
            tasks.append(asyncio.create_task(self._mouse_loop()))

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"[UNIFIED] Error: {e}")
            print("[UNIFIED] Refusing to die, restarting...")
            await asyncio.sleep(2)
            await self.start()

    def stop(self):
        self.running = False
        self.ear.stop()


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Unified Sensory System")
    parser.add_argument('--device', '-d', type=int, help='Audio device index')
    parser.add_argument('--list', '-l', action='store_true', help='List audio devices')
    parser.add_argument('--system', '-s', action='store_true', help='Use system audio')
    args = parser.parse_args()

    if args.list:
        list_devices()
        return

    device = args.device
    if args.system:
        device = find_monitor_device()
        if device:
            print(f"[UNIFIED] Using system audio (device {device})")

    unified = UnifiedSense(audio_device=device)

    try:
        await unified.start()
    except KeyboardInterrupt:
        print("\n[UNIFIED] Stopping...")
        unified.stop()


if __name__ == "__main__":
    asyncio.run(main())
