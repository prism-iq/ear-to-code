#!/usr/bin/env python3
"""
Export ear-to-code logs in AI-readable format
"""
import json
import sys
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).parent / "logs"


def format_for_ai(log_file: Path) -> str:
    """Convert JSONL log to AI-readable markdown"""
    lines = []
    current_song = None

    with open(log_file, 'r') as f:
        for line in f:
            try:
                event = json.loads(line)
                ts = event['timestamp']
                etype = event['event_type']
                data = event['data']

                if etype == 'song_detected':
                    current_song = f"{data.get('artist', '?')} - {data.get('title', '?')}"
                    lines.append(f"\n## [{ts}] Now Playing: {current_song}")
                    if data.get('album'):
                        lines.append(f"Album: {data['album']}")
                    if data.get('spotify'):
                        lines.append(f"Spotify: {data['spotify']}")

                elif etype == 'lyrics_sync':
                    lines.append(f"\n### Lyrics ({data.get('source', 'unknown')})")
                    lyrics = data.get('lyrics', '')
                    # Truncate for context window
                    if len(lyrics) > 2000:
                        lyrics = lyrics[:2000] + "\n[...]"
                    lines.append(lyrics)

                elif etype == 'audio_features':
                    bpm = data.get('estimated_bpm', 0)
                    bass = data.get('bass_ratio', 0) * 100
                    mid = data.get('mid_ratio', 0) * 100
                    high = data.get('high_ratio', 0) * 100
                    lines.append(f"\n[{ts}] Audio: ~{bpm:.0f}BPM | Bass:{bass:.0f}% Mid:{mid:.0f}% High:{high:.0f}%")

                elif etype == 'manual_correction':
                    lines.append(f"\n[{ts}] CORRECTION: Actually playing {data.get('artist')} - {data.get('title')}")

                elif etype == 'feedback_suggestion':
                    sugg = data.get('suggested', {})
                    lines.append(f"\n[{ts}] Suggestion from history: {sugg.get('artist')} - {sugg.get('title')}")

            except json.JSONDecodeError:
                continue

    return '\n'.join(lines)


def main():
    if len(sys.argv) > 1:
        log_file = Path(sys.argv[1])
    else:
        # Get most recent log
        logs = sorted(LOG_DIR.glob("ear_*.jsonl"))
        if not logs:
            print("No logs found")
            return
        log_file = logs[-1]

    print(f"# Audio Session Log")
    print(f"Source: {log_file.name}")
    print(f"Exported: {datetime.now().isoformat()}")
    print(format_for_ai(log_file))


if __name__ == "__main__":
    main()
