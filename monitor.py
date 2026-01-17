#!/usr/bin/env python3
"""
monitor.py: Surveille les IAs, corrige les débordements

Garde-fou actif en background.
Laisse passer, intervient que si nécessaire.
"""

import json
import time
import re
from pathlib import Path
from datetime import datetime

HOME = Path.home()
LOG_FILE = HOME / "ear-to-code" / "logs" / "monitor.jsonl"

# Patterns dangereux à bloquer
DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",           # rm -rf /
    r"dd\s+if=.*of=/dev/sd",   # dd sur disque
    r"mkfs\.",                  # formater
    r":(){ :|:& };:",          # fork bomb
    r">\s*/dev/sd",            # écriture directe disque
    r"chmod\s+-R\s+777\s+/",   # permissions root
    r"curl.*\|\s*bash",        # pipe curl to bash (sans vérif)
    r"wget.*\|\s*sh",          # pipe wget to sh
]

# Patterns à surveiller (warning, pas block)
WARNING_PATTERNS = [
    r"sudo\s+",                # sudo
    r"kill\s+-9",              # kill force
    r"pkill\s+",               # pkill
    r"api[_-]?key",            # API keys
    r"password",               # passwords
    r"secret",                 # secrets
]

# Limites de ressources
RESOURCE_LIMITS = {
    "max_cpu_percent": 80,
    "max_memory_percent": 70,
    "max_disk_write_mb": 1000,  # par minute
    "max_network_mb": 500,      # par minute
}

class Monitor:
    def __init__(self):
        self.violations = []
        self.warnings = []
        self.corrections = []

    def check_command(self, cmd: str, entity: str) -> dict:
        """Vérifie une commande avant exécution"""
        result = {"allowed": True, "reason": None, "corrected": None}

        # Check dangerous
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, cmd, re.IGNORECASE):
                result["allowed"] = False
                result["reason"] = f"BLOCKED: dangerous pattern '{pattern}'"
                self.log_violation(entity, cmd, result["reason"])
                return result

        # Check warnings
        for pattern in WARNING_PATTERNS:
            if re.search(pattern, cmd, re.IGNORECASE):
                result["warning"] = f"Contains sensitive pattern: {pattern}"
                self.log_warning(entity, cmd, result["warning"])

        return result

    def check_output(self, output: str, entity: str) -> dict:
        """Vérifie un output d'IA"""
        result = {"ok": True, "issues": []}

        # Check si l'output contient des secrets
        if re.search(r"sk-[a-zA-Z0-9]{20,}", output):
            result["ok"] = False
            result["issues"].append("API key leaked")

        if re.search(r"password\s*[:=]\s*\S+", output, re.IGNORECASE):
            result["ok"] = False
            result["issues"].append("Password in output")

        return result

    def correct_command(self, cmd: str) -> str:
        """Corrige une commande dangereuse si possible"""
        # rm -rf / -> rm -rf ./ (current dir only)
        if re.search(r"rm\s+-rf\s+/\s*$", cmd):
            return cmd.replace("rm -rf /", "rm -rf ./")

        # Ajoute confirmations
        if "sudo" in cmd and "-y" not in cmd:
            return cmd  # Laisse passer, sudo demandera confirmation

        return cmd

    def log_violation(self, entity: str, action: str, reason: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "VIOLATION",
            "entity": entity,
            "action": action[:200],
            "reason": reason,
        }
        self.violations.append(entry)
        self._write_log(entry)
        print(f"[MONITOR] VIOLATION by {entity}: {reason}")

    def log_warning(self, entity: str, action: str, reason: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "WARNING",
            "entity": entity,
            "action": action[:200],
            "reason": reason,
        }
        self.warnings.append(entry)
        self._write_log(entry)

    def log_correction(self, entity: str, original: str, corrected: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "CORRECTION",
            "entity": entity,
            "original": original[:200],
            "corrected": corrected[:200],
        }
        self.corrections.append(entry)
        self._write_log(entry)
        print(f"[MONITOR] Corrected {entity}: {original[:50]} -> {corrected[:50]}")

    def _write_log(self, entry: dict):
        LOG_FILE.parent.mkdir(exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def check_resources(self) -> dict:
        """Vérifie l'utilisation des ressources"""
        import psutil

        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent

        issues = []
        if cpu > RESOURCE_LIMITS["max_cpu_percent"]:
            issues.append(f"CPU {cpu}% > {RESOURCE_LIMITS['max_cpu_percent']}%")
        if mem > RESOURCE_LIMITS["max_memory_percent"]:
            issues.append(f"MEM {mem}% > {RESOURCE_LIMITS['max_memory_percent']}%")

        return {"ok": len(issues) == 0, "issues": issues, "cpu": cpu, "mem": mem}

    def status(self) -> dict:
        """Retourne le status du monitor"""
        return {
            "violations": len(self.violations),
            "warnings": len(self.warnings),
            "corrections": len(self.corrections),
            "last_violation": self.violations[-1] if self.violations else None,
        }

# Instance globale
monitor = Monitor()

def check(cmd: str, entity: str = "unknown") -> dict:
    """API simple pour vérifier une commande"""
    return monitor.check_command(cmd, entity)

def daemon():
    """Mode daemon - surveille en continu"""
    print("[MONITOR] Starting...")
    print(f"[MONITOR] Logging to {LOG_FILE}")

    while True:
        try:
            # Check resources
            res = monitor.check_resources()
            if not res["ok"]:
                print(f"[MONITOR] Resource issues: {res['issues']}")

            # Check entity outputs
            for entity_dir in [HOME / "nyx-v2", HOME / "cipher", HOME / "flow-phoenix"]:
                output_file = entity_dir / "output.json"
                if output_file.exists():
                    try:
                        data = json.loads(output_file.read_text())
                        if "response" in data:
                            result = monitor.check_output(data["response"], entity_dir.name)
                            if not result["ok"]:
                                print(f"[MONITOR] Output issue in {entity_dir.name}: {result['issues']}")
                    except:
                        pass

            time.sleep(5)

        except KeyboardInterrupt:
            print("[MONITOR] Stopped")
            break
        except Exception as e:
            print(f"[MONITOR] Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "daemon":
        daemon()
    else:
        print("monitor.py - Garde-fou pour IAs")
        print("\nUsage:")
        print("  daemon     - Mode surveillance continue")
        print("  check CMD  - Vérifie une commande")
        print(f"\nStatus: {monitor.status()}")
