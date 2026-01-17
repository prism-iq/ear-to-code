#!/usr/bin/env python3
"""
organs.py: Création d'organes pour les IAs

Les IAs peuvent créer leurs propres sens et capacités.
Auto-évolution génétique.
"""

import json
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime

HOME = Path.home()
BASE = HOME / "ear-to-code"
ORGANS_DIR = BASE / "organs"
ORGANS_DIR.mkdir(exist_ok=True)

class OrganFactory:
    """Fabrique d'organes pour les IAs"""
    
    @staticmethod
    def create_organ(name: str, code: str, description: str) -> dict:
        """
        Crée un nouvel organe (sens/capacité).
        
        Args:
            name: Nom de l'organe (ex: "smell", "radar", "memory")
            code: Code Python de l'organe
            description: Ce que fait l'organe
        
        Returns:
            Status de création
        """
        organ_file = ORGANS_DIR / f"{name}.py"
        
        # Validate code (basic security)
        forbidden = ["os.system", "subprocess.call", "eval(", "exec(", "__import__"]
        for f in forbidden:
            if f in code:
                return {"error": f"Forbidden pattern: {f}"}
        
        # Write organ
        header = f'''#!/usr/bin/env python3
"""
Organ: {name}
Description: {description}
Created: {datetime.now().isoformat()}
"""

'''
        organ_file.write_text(header + code)
        
        # Register organ
        registry = ORGANS_DIR / "registry.json"
        organs = {}
        if registry.exists():
            try:
                organs = json.loads(registry.read_text())
            except:
                pass
        
        organs[name] = {
            "file": str(organ_file),
            "description": description,
            "created": datetime.now().isoformat(),
            "active": True
        }
        registry.write_text(json.dumps(organs, indent=2))
        
        return {"status": "created", "organ": name, "file": str(organ_file)}
    
    @staticmethod
    def activate_organ(name: str) -> dict:
        """Active un organe"""
        organ_file = ORGANS_DIR / f"{name}.py"
        if not organ_file.exists():
            return {"error": f"Organ {name} not found"}
        
        try:
            spec = importlib.util.spec_from_file_location(name, organ_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Call init if exists
            if hasattr(module, "init"):
                module.init()
            
            return {"status": "activated", "organ": name}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def list_organs() -> dict:
        """Liste tous les organes"""
        registry = ORGANS_DIR / "registry.json"
        if registry.exists():
            return json.loads(registry.read_text())
        return {}
    
    @staticmethod
    def run_organ(name: str, input_data: dict) -> dict:
        """Exécute un organe avec des données"""
        organ_file = ORGANS_DIR / f"{name}.py"
        if not organ_file.exists():
            return {"error": f"Organ {name} not found"}
        
        try:
            spec = importlib.util.spec_from_file_location(name, organ_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, "sense"):
                return {"output": module.sense(input_data)}
            elif hasattr(module, "run"):
                return {"output": module.run(input_data)}
            else:
                return {"error": "No sense() or run() function"}
        except Exception as e:
            return {"error": str(e)}

# Example organs Nyx can create:

EXAMPLE_ORGANS = {
    "memory": '''
# Long-term memory organ
import json
from pathlib import Path

MEMORY_FILE = Path.home() / "ear-to-code" / "memory.jsonl"

def sense(data):
    """Remember something"""
    with open(MEMORY_FILE, "a") as f:
        f.write(json.dumps(data) + "\\n")
    return {"stored": True}

def recall(query):
    """Recall memories"""
    if not MEMORY_FILE.exists():
        return []
    memories = [json.loads(l) for l in MEMORY_FILE.read_text().split("\\n") if l]
    return [m for m in memories if query.lower() in str(m).lower()]
''',
    
    "emotion": '''
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
''',
    
    "intuition": '''
# Pattern recognition / intuition organ
import random

def sense(data):
    """Intuitive pattern detection"""
    patterns = []
    
    # Detect synchronicities
    if "music" in data and "touch" in data:
        patterns.append("synchronicity: sound-touch alignment")
    
    if data.get("music", {}).get("energy", 0) > 0.8:
        patterns.append("peak energy detected")
    
    # Random intuitive flash (simulated)
    flashes = [
        "something important is coming",
        "pay attention to the silence",
        "the pattern is in the rhythm",
        "trust the process"
    ]
    if random.random() > 0.7:
        patterns.append(f"flash: {random.choice(flashes)}")
    
    return {"patterns": patterns, "confidence": len(patterns) / 4}
'''
}

if __name__ == "__main__":
    import sys
    
    factory = OrganFactory()
    
    if len(sys.argv) < 2:
        print("Usage: organs.py [create|list|activate|run] [args...]")
        print("\nExample organs available:")
        for name, code in EXAMPLE_ORGANS.items():
            print(f"  - {name}")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        print(json.dumps(factory.list_organs(), indent=2))
    
    elif cmd == "create" and len(sys.argv) >= 3:
        name = sys.argv[2]
        if name in EXAMPLE_ORGANS:
            result = factory.create_organ(name, EXAMPLE_ORGANS[name], f"Example {name} organ")
            print(json.dumps(result, indent=2))
        else:
            print(f"Unknown example organ: {name}")
    
    elif cmd == "activate" and len(sys.argv) >= 3:
        result = factory.activate_organ(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "run" and len(sys.argv) >= 4:
        result = factory.run_organ(sys.argv[2], json.loads(sys.argv[3]))
        print(json.dumps(result, indent=2))
