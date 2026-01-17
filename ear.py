#!/usr/bin/env python3
"""
ear-to-code: Live audio capture, song recognition, lyrics scraping
Outputs timestamped logs for AI consumption
"""

import asyncio
import json
import hashlib
import struct
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Callable
import threading
import queue

# Audio capture
import sounddevice as sd
import numpy as np

# HTTP requests for APIs
import aiohttp

# Config
SAMPLE_RATE = 44100
CHANNELS = 1
CHUNK_DURATION = 5  # seconds per fingerprint chunk
BUFFER_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

# Low threshold for quiet systems (2dB encoded)
SILENCE_THRESHOLD = 0.001  # Very sensitive

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def list_devices():
    """List available audio devices"""
    print("\n[DEVICES] Available audio inputs:")
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            default = " (default)" if i == sd.default.device[0] else ""
            print(f"  {i}: {d['name']} [{d['max_input_channels']} in]{default}")
    print()


def find_monitor_device() -> Optional[int]:
    """Find pipewire/pulse monitor for system audio capture"""
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        name = d['name'].lower()
        # Prefer pipewire, then pulse
        if 'pipewire' in name and d['max_input_channels'] > 0:
            return i
        if 'pulse' in name and d['max_input_channels'] > 0:
            return i
    return None


@dataclass
class AudioEvent:
    timestamp: str
    unix_ts: float
    event_type: str  # "song_detected", "lyrics_sync", "audio_features"
    data: dict

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class AudioBuffer:
    """Thread-safe circular audio buffer"""
    def __init__(self, max_seconds: int = 30):
        self.buffer = np.zeros(SAMPLE_RATE * max_seconds, dtype=np.float32)
        self.write_pos = 0
        self.lock = threading.Lock()

    def write(self, data: np.ndarray):
        with self.lock:
            data = data.flatten()
            n = len(data)
            end_pos = self.write_pos + n
            if end_pos <= len(self.buffer):
                self.buffer[self.write_pos:end_pos] = data
            else:
                first_part = len(self.buffer) - self.write_pos
                self.buffer[self.write_pos:] = data[:first_part]
                self.buffer[:n - first_part] = data[first_part:]
            self.write_pos = end_pos % len(self.buffer)

    def read_last(self, seconds: float) -> np.ndarray:
        with self.lock:
            n = int(SAMPLE_RATE * seconds)
            start = (self.write_pos - n) % len(self.buffer)
            if start < self.write_pos:
                return self.buffer[start:self.write_pos].copy()
            else:
                return np.concatenate([
                    self.buffer[start:],
                    self.buffer[:self.write_pos]
                ])


class AudioAnalyzer:
    """Extract audio features - A-weighted, perceptual"""

    # A-weighting curve (simplified) - boosts bass perception
    A_WEIGHT = {
        20: -50.5, 31.5: -39.4, 63: -26.2, 125: -16.1, 250: -8.6,
        500: -3.2, 1000: 0, 2000: 1.2, 4000: 1.0, 8000: -1.1, 16000: -6.6
    }

    @staticmethod
    def a_weight(freq: float) -> float:
        """Get A-weighting for frequency"""
        keys = sorted(AudioAnalyzer.A_WEIGHT.keys())
        for i, k in enumerate(keys[:-1]):
            if keys[i] <= freq < keys[i+1]:
                # Linear interpolation
                ratio = (freq - keys[i]) / (keys[i+1] - keys[i])
                return AudioAnalyzer.A_WEIGHT[keys[i]] + ratio * (AudioAnalyzer.A_WEIGHT[keys[i+1]] - AudioAnalyzer.A_WEIGHT[keys[i]])
        return 0

    @staticmethod
    def get_features(audio: np.ndarray) -> dict:
        """Extract perceptual audio features"""
        if len(audio) == 0:
            return {}

        # RMS (volume) with pre-emphasis for bass
        rms = np.sqrt(np.mean(audio ** 2))

        # FFT
        fft = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1/SAMPLE_RATE)

        # Band energies with perceptual weighting (boost bass)
        bass_mask = (freqs >= 20) & (freqs < 250)
        mid_mask = (freqs >= 250) & (freqs < 4000)
        high_mask = (freqs >= 4000) & (freqs < 20000)

        # Apply perceptual curve - bass x4, mid x1, high x0.5
        bass = np.sum(fft[bass_mask] ** 2) * 4.0
        mid = np.sum(fft[mid_mask] ** 2) * 1.0
        high = np.sum(fft[high_mask] ** 2) * 0.5
        total = bass + mid + high + 1e-10

        # Dominant frequency (weighted toward bass)
        weighted_fft = fft.copy()
        weighted_fft[bass_mask] *= 2.0
        dominant_idx = np.argmax(weighted_fft)
        dominant_freq = freqs[dominant_idx] if dominant_idx < len(freqs) else 0

        # Beat detection - onset detection function
        window = int(SAMPLE_RATE * 0.05)  # 50ms windows
        hop = window // 2
        energies = []
        for i in range(0, len(audio) - window, hop):
            # Focus on bass for beat detection
            chunk = audio[i:i+window]
            chunk_fft = np.abs(np.fft.rfft(chunk))
            chunk_freqs = np.fft.rfftfreq(len(chunk), 1/SAMPLE_RATE)
            bass_energy = np.sum(chunk_fft[(chunk_freqs >= 20) & (chunk_freqs < 200)] ** 2)
            energies.append(bass_energy)

        if len(energies) > 2:
            energies = np.array(energies)
            # Spectral flux (onset strength)
            flux = np.diff(energies)
            flux = np.maximum(flux, 0)  # Only positive changes (onsets)
            threshold = np.mean(flux) + np.std(flux)
            beats = np.sum(flux > threshold)
            duration = len(audio) / SAMPLE_RATE
            estimated_bpm = (beats / duration) * 60 * 0.5  # Adjust for typical music
            estimated_bpm = np.clip(estimated_bpm, 0, 200)
        else:
            estimated_bpm = 0

        # Zero crossing (texture)
        zcr = np.sum(np.abs(np.diff(np.sign(audio)))) / (2 * len(audio))

        return {
            "rms": float(rms),
            "zcr": float(zcr),
            "bass_ratio": float(bass / total),
            "mid_ratio": float(mid / total),
            "high_ratio": float(high / total),
            "dominant_freq": float(dominant_freq),
            "estimated_bpm": float(estimated_bpm),
        }


class SongRecognizer:
    """Recognize songs using audio fingerprinting APIs"""

    def __init__(self):
        # AudD API (free tier available)
        self.audd_token = None  # Set via env: AUDD_API_TOKEN
        # Shazam via RapidAPI
        self.shazam_key = None  # Set via env: SHAZAM_API_KEY

        self.last_song = None
        self.last_recognition_time = 0
        self.cooldown = 10  # seconds between recognition attempts

    async def recognize(self, audio: np.ndarray, session: aiohttp.ClientSession) -> Optional[dict]:
        """Try to recognize the song from audio"""
        now = time.time()
        if now - self.last_recognition_time < self.cooldown:
            return None

        self.last_recognition_time = now

        # Convert to WAV bytes
        wav_data = self._to_wav(audio)

        # Try AudD first
        result = await self._try_audd(wav_data, session)
        if result:
            return result

        # Fallback to Shazam
        result = await self._try_shazam(wav_data, session)
        return result

    def _to_wav(self, audio: np.ndarray) -> bytes:
        """Convert numpy audio to WAV bytes"""
        import io
        import wave

        # Normalize and convert to int16
        audio = np.clip(audio, -1, 1)
        audio_int16 = (audio * 32767).astype(np.int16)

        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav:
            wav.setnchannels(CHANNELS)
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(audio_int16.tobytes())

        return buffer.getvalue()

    async def _try_audd(self, wav_data: bytes, session: aiohttp.ClientSession) -> Optional[dict]:
        """Try AudD API"""
        import os
        token = os.environ.get('AUDD_API_TOKEN', self.audd_token)
        if not token:
            return None

        try:
            data = aiohttp.FormData()
            data.add_field('api_token', token)
            data.add_field('file', wav_data, filename='audio.wav', content_type='audio/wav')
            data.add_field('return', 'lyrics,spotify')

            async with session.post('https://api.audd.io/', data=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get('status') == 'success' and result.get('result'):
                        r = result['result']
                        return {
                            'source': 'audd',
                            'title': r.get('title'),
                            'artist': r.get('artist'),
                            'album': r.get('album'),
                            'release_date': r.get('release_date'),
                            'lyrics': r.get('lyrics', {}).get('lyrics'),
                            'spotify': r.get('spotify', {}).get('external_urls', {}).get('spotify'),
                        }
        except Exception as e:
            print(f"[AudD Error] {e}")
        return None

    async def _try_shazam(self, wav_data: bytes, session: aiohttp.ClientSession) -> Optional[dict]:
        """Try Shazam via RapidAPI"""
        import os
        import base64

        key = os.environ.get('SHAZAM_API_KEY', self.shazam_key)
        if not key:
            return None

        try:
            headers = {
                'X-RapidAPI-Key': key,
                'X-RapidAPI-Host': 'shazam.p.rapidapi.com',
                'Content-Type': 'text/plain',
            }

            audio_b64 = base64.b64encode(wav_data).decode()

            async with session.post(
                'https://shazam.p.rapidapi.com/songs/detect',
                headers=headers,
                data=audio_b64
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get('track'):
                        t = result['track']
                        return {
                            'source': 'shazam',
                            'title': t.get('title'),
                            'artist': t.get('subtitle'),
                            'album': t.get('sections', [{}])[0].get('metadata', [{}])[0].get('text'),
                            'shazam_url': t.get('url'),
                        }
        except Exception as e:
            print(f"[Shazam Error] {e}")
        return None


class LyricsScraper:
    """Scrape lyrics from various sources"""

    def __init__(self):
        self.genius_token = None  # Set via env: GENIUS_API_TOKEN
        self.cache = {}

    async def get_lyrics(self, title: str, artist: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Get lyrics for a song"""
        cache_key = f"{artist}:{title}".lower()
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Try Genius first
        lyrics = await self._try_genius(title, artist, session)
        if lyrics:
            self.cache[cache_key] = lyrics
            return lyrics

        # Try lyrics.ovh (free, no API key)
        lyrics = await self._try_lyrics_ovh(title, artist, session)
        if lyrics:
            self.cache[cache_key] = lyrics
            return lyrics

        return None

    async def _try_genius(self, title: str, artist: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Try Genius API"""
        import os
        token = os.environ.get('GENIUS_API_TOKEN', self.genius_token)
        if not token:
            return None

        try:
            headers = {'Authorization': f'Bearer {token}'}
            params = {'q': f'{artist} {title}'}

            async with session.get(
                'https://api.genius.com/search',
                headers=headers,
                params=params
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    hits = data.get('response', {}).get('hits', [])
                    if hits:
                        # Get lyrics page URL
                        url = hits[0]['result']['url']
                        # Scrape lyrics from page
                        return await self._scrape_genius_page(url, session)
        except Exception as e:
            print(f"[Genius Error] {e}")
        return None

    async def _scrape_genius_page(self, url: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Scrape lyrics from Genius page"""
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    # Simple extraction - look for lyrics container
                    import re
                    # Genius uses data-lyrics-container
                    matches = re.findall(r'data-lyrics-container="true"[^>]*>(.*?)</div>', html, re.DOTALL)
                    if matches:
                        lyrics = ' '.join(matches)
                        # Clean HTML tags
                        lyrics = re.sub(r'<[^>]+>', '\n', lyrics)
                        lyrics = re.sub(r'&[^;]+;', '', lyrics)
                        return lyrics.strip()
        except Exception as e:
            print(f"[Genius Scrape Error] {e}")
        return None

    async def _try_lyrics_ovh(self, title: str, artist: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Try lyrics.ovh API (free, no key needed)"""
        try:
            url = f'https://api.lyrics.ovh/v1/{artist}/{title}'
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('lyrics')
        except Exception as e:
            print(f"[Lyrics.ovh Error] {e}")
        return None


class FeedbackLearner:
    """Track recognition errors and learn from corrections"""

    def __init__(self):
        self.feedback_file = LOG_DIR / "feedback_history.jsonl"
        self.corrections = {}  # fingerprint_hash -> correct_song
        self.error_patterns = []  # List of {features, wrong, correct}
        self._load_history()

    def _load_history(self):
        """Load previous corrections"""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r') as f:
                    for line in f:
                        entry = json.loads(line)
                        if entry.get('type') == 'correction':
                            self.error_patterns.append(entry)
            except Exception as e:
                print(f"[Feedback] Error loading history: {e}")

    def record_error(self, features: dict, recognized: Optional[dict], correct: dict, audio_hash: str):
        """Record a recognition error for learning"""
        entry = {
            "type": "correction",
            "timestamp": datetime.now().isoformat(),
            "audio_hash": audio_hash,
            "features": features,
            "recognized": recognized,
            "correct": correct,
        }
        self.error_patterns.append(entry)

        # Save to file
        with open(self.feedback_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

        print(f"[Feedback] Recorded correction: {recognized} -> {correct}")

    def get_similar_corrections(self, features: dict) -> list:
        """Find past corrections with similar audio features"""
        if not features or not self.error_patterns:
            return []

        similar = []
        for pattern in self.error_patterns:
            if not pattern.get('features'):
                continue
            # Compare key features
            score = 0
            pf = pattern['features']
            if abs(features.get('bass_ratio', 0) - pf.get('bass_ratio', 0)) < 0.1:
                score += 1
            if abs(features.get('mid_ratio', 0) - pf.get('mid_ratio', 0)) < 0.1:
                score += 1
            if abs(features.get('estimated_bpm', 0) - pf.get('estimated_bpm', 0)) < 10:
                score += 2
            if score >= 2:
                similar.append(pattern)

        return similar

    def suggest_from_history(self, features: dict) -> Optional[dict]:
        """Suggest a song based on similar past corrections"""
        similar = self.get_similar_corrections(features)
        if similar:
            # Return most recent similar correction
            return similar[-1].get('correct')
        return None


class EarToCode:
    """Main class: listen, recognize, log for AI consumption"""

    def __init__(self, device: Optional[int] = None):
        self.buffer = AudioBuffer(max_seconds=30)
        self.analyzer = AudioAnalyzer()
        self.recognizer = SongRecognizer()
        self.lyrics_scraper = LyricsScraper()
        self.feedback = FeedbackLearner()

        self.device = device
        self.running = False
        self.event_queue = queue.Queue()
        self.current_song = None
        self.last_features = {}
        self.last_audio_hash = ""

        # Heartbeat - proves the ear is alive
        self.last_heartbeat = time.time()
        self.heartbeat_interval = 5  # seconds
        self.stream_failures = 0
        self.max_failures = 10

        # Log file
        self.log_file = LOG_DIR / f"ear_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

        # Persistent state file (survives crashes)
        self.state_file = LOG_DIR / "ear_state.json"

        # Callbacks for external systems
        self.on_event: Optional[Callable[[AudioEvent], None]] = None

    def _save_state(self):
        """Save current state to disk (survives crashes)"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "alive": True,
            "current_song": self.current_song,
            "log_file": str(self.log_file),
            "stream_failures": self.stream_failures,
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f)

    def _heartbeat(self):
        """Emit heartbeat to prove the ear is alive"""
        now = time.time()
        if now - self.last_heartbeat >= self.heartbeat_interval:
            self.last_heartbeat = now
            self._emit_event("heartbeat", {
                "alive": True,
                "uptime_seconds": now - self.start_time,
                "stream_failures": self.stream_failures,
                "current_song": self.current_song.get('title') if self.current_song else None,
            })
            self._save_state()

    def _audio_callback(self, indata, frames, time_info, status):
        """Called by sounddevice for each audio chunk"""
        if status:
            print(f"[Audio Status] {status}")
            self.stream_failures += 1
        self.buffer.write(indata[:, 0] if indata.ndim > 1 else indata)
        self._heartbeat()

    def _emit_event(self, event_type: str, data: dict):
        """Create and emit an event"""
        event = AudioEvent(
            timestamp=datetime.now().isoformat(),
            unix_ts=time.time(),
            event_type=event_type,
            data=data
        )

        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write(event.to_json() + '\n')

        # Callback
        if self.on_event:
            self.on_event(event)

        # Print to stdout for piping
        print(event.to_json())

    async def _process_loop(self):
        """Main processing loop"""
        async with aiohttp.ClientSession() as session:
            while self.running:
                try:
                    # Get last 5 seconds of audio
                    audio = self.buffer.read_last(CHUNK_DURATION)

                    if np.max(np.abs(audio)) < SILENCE_THRESHOLD:
                        # Silence, skip processing
                        await asyncio.sleep(1)
                        continue

                    # Compute audio hash for feedback tracking
                    self.last_audio_hash = hashlib.md5(audio.tobytes()[:10000]).hexdigest()[:16]

                    # Extract features
                    features = self.analyzer.get_features(audio)
                    self.last_features = features
                    self._emit_event("audio_features", features)

                    # Check feedback history first
                    suggestion = self.feedback.suggest_from_history(features)
                    if suggestion:
                        self._emit_event("feedback_suggestion", {
                            "suggested": suggestion,
                            "confidence": "from_history"
                        })

                    # Try to recognize song
                    song = await self.recognizer.recognize(audio, session)
                    if song and song != self.current_song:
                        self.current_song = song
                        self._emit_event("song_detected", song)

                        # Get lyrics
                        if song.get('title') and song.get('artist'):
                            # Check if lyrics already in recognition result
                            if song.get('lyrics'):
                                self._emit_event("lyrics_sync", {
                                    "title": song['title'],
                                    "artist": song['artist'],
                                    "lyrics": song['lyrics'],
                                    "source": "recognition"
                                })
                            else:
                                lyrics = await self.lyrics_scraper.get_lyrics(
                                    song['title'], song['artist'], session
                                )
                                if lyrics:
                                    self._emit_event("lyrics_sync", {
                                        "title": song['title'],
                                        "artist": song['artist'],
                                        "lyrics": lyrics,
                                        "source": "scraper"
                                    })

                    await asyncio.sleep(2)  # Process every 2 seconds

                except Exception as e:
                    print(f"[Process Error] {e}")
                    await asyncio.sleep(1)

    async def start(self):
        """Start listening - NEVER DIES, auto-reconnects"""
        self.running = True
        self.start_time = time.time()

        print(f"[EAR] Starting audio capture...")
        print(f"[EAR] Log file: {self.log_file}")
        print(f"[EAR] Sample rate: {SAMPLE_RATE}Hz, Channels: {CHANNELS}")
        print(f"[EAR] Mode: PERSISTENT (auto-reconnect enabled)")

        # Check for API keys
        import os
        if not os.environ.get('AUDD_API_TOKEN') and not os.environ.get('SHAZAM_API_KEY'):
            print("[WARN] No recognition API key set. Set AUDD_API_TOKEN or SHAZAM_API_KEY")
        if not os.environ.get('GENIUS_API_TOKEN'):
            print("[WARN] No GENIUS_API_TOKEN set. Will use lyrics.ovh fallback")

        # Persistent loop - NEVER exits unless explicitly stopped
        while self.running:
            try:
                # Start audio stream
                stream = sd.InputStream(
                    device=self.device,
                    samplerate=SAMPLE_RATE,
                    channels=CHANNELS,
                    dtype=np.float32,
                    callback=self._audio_callback,
                    blocksize=int(SAMPLE_RATE * 0.1)  # 100ms blocks
                )

                with stream:
                    self._emit_event("stream_connected", {
                        "device": self.device,
                        "reconnect_count": self.stream_failures
                    })
                    print("[EAR] Listening... (CTRL+C to stop)")
                    await self._process_loop()

            except sd.PortAudioError as e:
                self.stream_failures += 1
                self._emit_event("stream_error", {
                    "error": str(e),
                    "failures": self.stream_failures,
                    "will_retry": self.stream_failures < self.max_failures
                })
                print(f"[EAR] Stream error #{self.stream_failures}: {e}")

                if self.stream_failures >= self.max_failures:
                    print("[EAR] Too many failures, but REFUSING TO DIE. Waiting 30s...")
                    await asyncio.sleep(30)
                    self.stream_failures = 0  # Reset and try again
                else:
                    print(f"[EAR] Reconnecting in 2s...")
                    await asyncio.sleep(2)

            except Exception as e:
                self._emit_event("critical_error", {"error": str(e), "type": type(e).__name__})
                print(f"[EAR] Critical error: {e}")
                print("[EAR] Refusing to die. Reconnecting in 5s...")
                await asyncio.sleep(5)

    def stop(self):
        """Stop listening"""
        self.running = False

    def correct(self, title: str, artist: str):
        """Manually correct the last recognition"""
        correct_song = {"title": title, "artist": artist, "source": "manual_correction"}
        self.feedback.record_error(
            features=self.last_features,
            recognized=self.current_song,
            correct=correct_song,
            audio_hash=self.last_audio_hash
        )
        self.current_song = correct_song
        self._emit_event("manual_correction", correct_song)


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="ear-to-code: Audio listener for AI")
    parser.add_argument('--device', '-d', type=int, help='Audio device index')
    parser.add_argument('--list', '-l', action='store_true', help='List audio devices')
    parser.add_argument('--system', '-s', action='store_true', help='Capture system audio (pipewire)')
    args = parser.parse_args()

    if args.list:
        list_devices()
        return

    device = args.device
    if args.system:
        device = find_monitor_device()
        if device is None:
            print("[ERROR] No pipewire/pulse monitor found")
            return
        print(f"[EAR] Using system audio capture (device {device})")

    ear = EarToCode(device=device)

    # Interactive correction via stdin (non-blocking)
    async def input_handler():
        import sys
        import select
        while ear.running:
            # Check if input available
            if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
                line = sys.stdin.readline().strip()
                if line.startswith("correct:"):
                    # Format: correct:Artist - Title
                    parts = line[8:].split(" - ", 1)
                    if len(parts) == 2:
                        ear.correct(title=parts[1], artist=parts[0])
                    else:
                        print("[HELP] Format: correct:Artist - Title")
            await asyncio.sleep(0.1)

    try:
        await asyncio.gather(
            ear.start(),
            input_handler()
        )
    except KeyboardInterrupt:
        print("\n[EAR] Stopping...")
        ear.stop()


if __name__ == "__main__":
    asyncio.run(main())
