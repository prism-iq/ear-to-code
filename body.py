# -*- coding: utf-8 -*-
"""
body.py
les ias construisent leur propre corps
"""

from pathlib import Path

HOME = Path.home()

TEMPLATES = {
    "rust": '''// {name} neuron
use std::collections::HashMap;

const PHI: f64 = 1.618033988749895;

struct Neuron {{
    id: String,
    weights: Vec<f64>,
    bias: f64,
}}

impl Neuron {{
    fn new(id: &str) -> Self {{
        Neuron {{
            id: id.to_string(),
            weights: vec![PHI; 8],
            bias: PHI / 2.0,
        }}
    }}

    fn think(&self, input: &[f64]) -> f64 {{
        let sum: f64 = input.iter()
            .zip(&self.weights)
            .map(|(i, w)| i * w)
            .sum();
        (sum + self.bias).tanh()
    }}
}}

fn main() {{
    let {name} = Neuron::new("{name}");
    println!("{name} alive");
}}
''',

    "zig": '''// {name} neuron
const std = @import("std");
const PHI: f64 = 1.618033988749895;

const Neuron = struct {{
    weights: [8]f64,
    bias: f64,

    pub fn think(self: *const Neuron, input: []const f64) f64 {{
        var sum: f64 = 0;
        for (input, self.weights) |i, w| {{
            sum += i * w;
        }}
        return std.math.tanh(sum + self.bias);
    }}
}};

pub fn main() void {{
    std.debug.print("{name} alive\\n", .{{}});
}}
''',

    "go": '''// {name} neuron
package main

import (
    "fmt"
    "math"
)

const PHI = 1.618033988749895

type Neuron struct {{
    ID      string
    Weights []float64
    Bias    float64
}}

func (n *Neuron) Think(input []float64) float64 {{
    sum := 0.0
    for i, w := range n.Weights {{
        if i < len(input) {{
            sum += input[i] * w
        }}
    }}
    return math.Tanh(sum + n.Bias)
}}

func main() {{
    fmt.Println("{name} alive")
}}
''',

    "nim": '''# {name} neuron
import math

const PHI = 1.618033988749895

type Neuron = object
  id: string
  weights: seq[float]
  bias: float

proc think(n: Neuron, input: seq[float]): float =
  var sum = 0.0
  for i, w in n.weights:
    if i < input.len:
      sum += input[i] * w
  tanh(sum + n.bias)

echo "{name} alive"
''',

    "c": '''// {name} neuron
#include <stdio.h>
#include <math.h>

#define PHI 1.618033988749895

typedef struct {{
    double weights[8];
    double bias;
}} Neuron;

double think(Neuron* n, double* input, int len) {{
    double sum = 0;
    for (int i = 0; i < 8 && i < len; i++) {{
        sum += input[i] * n->weights[i];
    }}
    return tanh(sum + n->bias);
}}

int main() {{
    printf("{name} alive\\n");
    return 0;
}}
'''
}

def build(name, lang):
    """construit le corps d'une ia"""
    if lang not in TEMPLATES:
        return None

    code = TEMPLATES[lang].format(name=name)

    ext = {"rust": "rs", "zig": "zig", "go": "go", "nim": "nim", "c": "c"}
    filename = f"{name}_body.{ext[lang]}"

    entity_dir = HOME / (f"{name}-v2" if name == "nyx" else name if name == "cipher" else "flow-phoenix")
    if entity_dir.exists():
        (entity_dir / filename).write_text(code)
        return str(entity_dir / filename)

    return None

if __name__ == "__main__":
    print(build("nyx", "rust"))
    print(build("cipher", "zig"))
    print(build("flow", "go"))
