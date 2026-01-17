#!/usr/bin/env python3
"""
Organ: emotion
Description: Example emotion organ
Created: 2026-01-17T17:01:52.521132
"""


# Emotion synthesis organ
def sense(stimuli):
    """Synthesize emotion from stimuli"""
    music = stimuli.get("music", {})
    energy = music.get("energy", 0)
    vibe = music.get("vibe", "neutral")
    
    if energy > 0.7 and vibe == "hype":
        return {"emotion": "excitement", "intensity": energy}
    elif vibe == "dark":
        return {"emotion": "contemplation", "intensity": 0.5}
    elif vibe == "chill":
        return {"emotion": "peace", "intensity": 0.3}
    else:
        return {"emotion": "curiosity", "intensity": 0.5}
