"""Executa as suítes independentes dos três projetos."""
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parent
    failures = 0
    for project in ("focus-flow", "file-garden", "habit-bloom"):
        print(f"\n=== {project} ===", flush=True)
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-v"], cwd=root / "projects" / project)
        failures += result.returncode != 0
    return int(failures > 0)


if __name__ == "__main__":
    raise SystemExit(main())
