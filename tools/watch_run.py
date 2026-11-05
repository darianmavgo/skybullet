#!/usr/bin/env python3
"""Dev loop: run the game and restart it whenever a script/scene/resource/.glb changes.

  python3 tools/watch_run.py            # from the repo root

Restart-based reload (no editor needed). Game log goes to stdout; Ctrl+C quits.
"""
import subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GODOT = "/Applications/Godot.app/Contents/MacOS/Godot"
WATCH = ["scripts", "scenes", "resources", "assets/models"]
EXTS = {".gd", ".tscn", ".tres", ".glb", ".gdshader"}


def snapshot():
    snap = {}
    for d in WATCH:
        for p in (ROOT / d).rglob("*"):
            if p.suffix in EXTS:
                snap[p] = p.stat().st_mtime
    return snap


def launch():
    print("[watch] launching game", flush=True)
    return subprocess.Popen([GODOT, "--path", str(ROOT)] + sys.argv[1:])


proc, last = launch(), snapshot()
try:
    while True:
        time.sleep(0.5)
        now = snapshot()
        if now != last:
            changed = [p.name for p in now if now[p] != last.get(p)] or ["(removed file)"]
            print("[watch] changed:", ", ".join(changed[:5]), "-> restarting", flush=True)
            time.sleep(0.3)  # let writes finish
            proc.terminate(); proc.wait()
            proc, last = launch(), snapshot()
        elif proc.poll() is not None:
            print("[watch] game exited; waiting for a change", flush=True)
            while snapshot() == last:
                time.sleep(0.5)
except KeyboardInterrupt:
    proc.terminate()
