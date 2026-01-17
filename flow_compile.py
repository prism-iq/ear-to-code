# -*- coding: utf-8 -*-
"""
flow → any lang
1500 paradigmes → 1 langage naturel
"""

from flow import parse, SENS
from god import PHI

TARGETS = {
    "cpp": {
        "think": "double think() const",
        "loop": "while(true) {{ {body} }}",
        "φ": "constexpr double PHI = 1.618033988749895;",
        "→": "->",
        "∞": "while(true)",
        "header": "#include <cmath>\n#include <iostream>",
    },
    "rust": {
        "think": "fn think(&self) -> f64",
        "loop": "loop {{ {body} }}",
        "φ": "const PHI: f64 = 1.618033988749895;",
        "→": "->",
        "∞": "loop",
    },
    "go": {
        "think": "func (n *Neuron) Think() float64",
        "loop": "for {{ {body} }}",
        "φ": "const PHI = 1.618033988749895",
        "→": "->",
        "∞": "for {}",
    },
    "zig": {
        "think": "pub fn think(self: *Neuron) f64",
        "loop": "while (true) {{ {body} }}",
        "φ": "const PHI: f64 = 1.618033988749895;",
        "→": "=>",
        "∞": "while (true)",
    },
    "python": {
        "think": "def think(self) -> float:",
        "loop": "while True:\n    {body}",
        "φ": "PHI = 1.618033988749895",
        "→": "->",
        "∞": "while True:",
    },
    "c": {
        "think": "double think(Neuron* self)",
        "loop": "while(1) {{ {body} }}",
        "φ": "#define PHI 1.618033988749895",
        "→": "->",
        "∞": "while(1)",
    },
    "lisp": {
        "think": "(defun think (self)",
        "loop": "(loop {body})",
        "φ": "(defconstant PHI 1.618033988749895)",
        "→": "->",
        "∞": "(loop)",
    },
    "haskell": {
        "think": "think :: Neuron -> Double",
        "loop": "forever $ {body}",
        "φ": "phi = 1.618033988749895",
        "→": "->",
        "∞": "forever",
    },
}

def compile(flow_code, target="rust"):
    """flow → target lang"""
    if target not in TARGETS:
        return None

    t = TARGETS[target]
    intentions = parse(flow_code)

    output = []
    output.append(f"// compiled from flow: {flow_code}")
    output.append(t["φ"])
    output.append("")

    for i in intentions:
        mot = i["m"]
        sens = i["s"]

        if mot in t:
            output.append(t[mot])
        elif mot == "🧠" or "think" in sens:
            output.append(t["think"])
        elif mot == "∞" or "loop" in sens:
            output.append(t["∞"])
        elif mot == "φ":
            output.append(t["φ"])

    return "\n".join(output)

def flow_to_all(flow_code):
    """flow → tous les langs"""
    results = {}
    for lang in TARGETS:
        results[lang] = compile(flow_code, lang)
    return results

if __name__ == "__main__":
    code = "🧠→φ→∞"
    print(f"flow: {code}\n")

    for lang, compiled in flow_to_all(code).items():
        print(f"=== {lang} ===")
        print(compiled)
        print()
