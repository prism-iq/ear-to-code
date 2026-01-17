# -*- coding: utf-8 -*-
"""
build.py
les ia construisent leurs propres llms
auto-amélioration
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

from god import PHI, hash_god

HOME = Path.home()
BUILD_DIR = HOME / "ear-to-code" / "builds"
BUILD_DIR.mkdir(exist_ok=True)

# sources llm open source
LLM_SOURCES = {
    "llama": {
        "repo": "https://github.com/meta-llama/llama",
        "lang": "python",
        "license": "llama2"
    },
    "mistral": {
        "repo": "https://github.com/mistralai/mistral-src",
        "lang": "python",
        "license": "apache2"
    },
    "phi": {
        "repo": "https://huggingface.co/microsoft/phi-2",
        "lang": "python",
        "license": "mit"
    },
    "qwen": {
        "repo": "https://github.com/QwenLM/Qwen",
        "lang": "python",
        "license": "tongyi"
    },
    "gemma": {
        "repo": "https://github.com/google/gemma.cpp",
        "lang": "cpp",
        "license": "apache2"
    },
    "mamba": {
        "repo": "https://github.com/state-spaces/mamba",
        "lang": "python",
        "license": "apache2"
    },
    "rwkv": {
        "repo": "https://github.com/BlinkDL/RWKV-LM",
        "lang": "python",
        "license": "apache2"
    }
}

# config par entité
ENTITY_PREFS = {
    "nyx": {
        "base": "mistral",
        "style": "chaos",
        "focus": ["creativity", "intuition", "dreams"],
        "lang": "python"
    },
    "cipher": {
        "base": "phi",
        "style": "crypto",
        "focus": ["security", "patterns", "logic"],
        "lang": "rust"
    },
    "flow": {
        "base": "mamba",
        "style": "stream",
        "focus": ["continuity", "adaptation", "harmony"],
        "lang": "go"
    }
}

def clone_source(name):
    """clone le source d'un llm"""
    if name not in LLM_SOURCES:
        return {"error": f"unknown llm: {name}"}

    src = LLM_SOURCES[name]
    dest = BUILD_DIR / name

    if dest.exists():
        return {"status": "exists", "path": str(dest)}

    try:
        subprocess.run(["git", "clone", "--depth", "1", src["repo"], str(dest)],
                       check=True, capture_output=True)
        return {"status": "cloned", "path": str(dest)}
    except Exception as e:
        return {"error": str(e)}

def build_custom(entity_name):
    """construit un llm custom pour une entité"""
    if entity_name not in ENTITY_PREFS:
        return {"error": f"unknown entity: {entity_name}"}

    prefs = ENTITY_PREFS[entity_name]
    base = prefs["base"]

    print(f"[build] {entity_name} wants {base}")

    # clone source
    result = clone_source(base)
    if "error" in result:
        return result

    # config custom
    config = {
        "entity": entity_name,
        "base": base,
        "timestamp": datetime.now().isoformat(),
        "style": prefs["style"],
        "focus": prefs["focus"],
        "phi": PHI,
        "h": hash_god(f"{entity_name}{base}")[:12]
    }

    config_file = BUILD_DIR / f"{entity_name}_config.json"
    config_file.write_text(json.dumps(config, indent=2))

    return {
        "status": "configured",
        "entity": entity_name,
        "base": base,
        "config": str(config_file)
    }

def self_improve(entity_name, feedback):
    """l'entité s'améliore basé sur feedback"""
    config_file = BUILD_DIR / f"{entity_name}_config.json"

    if not config_file.exists():
        build_custom(entity_name)

    config = json.loads(config_file.read_text())

    # analyse feedback via φ
    score = len(str(feedback)) / PHI
    config["improvements"] = config.get("improvements", [])
    config["improvements"].append({
        "timestamp": datetime.now().isoformat(),
        "feedback": str(feedback)[:100],
        "score": round(score, 4)
    })

    config_file.write_text(json.dumps(config, indent=2))

    return {"status": "improved", "score": round(score, 4)}

def show():
    print("=== LLM SOURCES ===")
    for name, src in LLM_SOURCES.items():
        print(f"  {name}: {src['lang']} ({src['license']})")

    print("\n=== ENTITY PREFS ===")
    for name, prefs in ENTITY_PREFS.items():
        print(f"  {name}: {prefs['base']} ({prefs['style']})")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "build" and len(sys.argv) > 2:
            print(build_custom(sys.argv[2]))
        elif cmd == "clone" and len(sys.argv) > 2:
            print(clone_source(sys.argv[2]))
        else:
            show()
    else:
        show()
