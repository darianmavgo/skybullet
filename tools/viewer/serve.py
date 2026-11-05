#!/usr/bin/env python3
"""Sky Bullet dev dashboard with hot reload.  Run:  python3 tools/viewer/serve.py  -> http://127.0.0.1:8765

Shows schematics (docs/img/*.svg), 3D models (assets/models/**/*.glb), the range-budget sim table,
and build logs. Watches files: editing blender/scripts/build_*.py re-runs headless Blender and
re-exports the .glb; editing sim/*.py or docs/img/*.svg refreshes the page. Local only (127.0.0.1),
serves an allowlist of folders (never .env).
"""
import json, subprocess, threading, time, mimetypes, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent.parent
VIEW = Path(__file__).resolve().parent
BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
SERVED = ("docs/img/", "assets/models/")       # allowlisted URL prefixes
SERVED_EXT = {".svg", ".glb", ".png", ".html"}
PORT = 8765

state = {"builds": {}, "lock": threading.Lock()}


def watched():
    files = list((ROOT / "blender/scripts").glob("*.py")) + list((ROOT / "sim").glob("*.py"))
    files += list((ROOT / "docs/img").glob("*.svg")) + list((ROOT / "assets/models").rglob("*.glb"))
    files += list(VIEW.glob("*.html"))
    return files


def stamp():
    return max((f.stat().st_mtime for f in watched() if f.exists()), default=0)


def run_build(script):
    t0 = time.time()
    if not Path(BLENDER).exists():
        out = "Blender not found at " + BLENDER
    else:
        p = subprocess.run([BLENDER, "--background", "--python", str(script)], capture_output=True, text=True, cwd=ROOT, timeout=300)
        lines = [l for l in (p.stdout + p.stderr).splitlines() if "WROTE" in l or "Error" in l or "Traceback" in l or l.startswith("  File")]
        out = "\n".join(lines) or "(no output)"
    with state["lock"]:
        state["builds"][script.name] = {"when": time.strftime("%H:%M:%S"), "secs": round(time.time() - t0, 1), "log": out}
    print(f"[build] {script.name}: {out.splitlines()[-1] if out else ''}", flush=True)


def watcher():
    scripts = lambda: sorted((ROOT / "blender/scripts").glob("build_*.py"))
    seen = {p: p.stat().st_mtime for p in scripts()}
    common = (ROOT / "blender/scripts/bs_common.py")
    common_seen = common.stat().st_mtime if common.exists() else 0
    while True:
        time.sleep(1)
        try:
            cm = common.stat().st_mtime if common.exists() else 0
            for p in scripts():
                m = p.stat().st_mtime
                if m != seen.get(p) or cm != common_seen:
                    seen[p] = m
                    run_build(p)
            common_seen = cm
        except Exception as e:  # keep watching no matter what
            print("[watch]", e, flush=True)


def sim_text():
    p = subprocess.run([sys.executable, "-I", str(ROOT / "sim/range_budget.py")], capture_output=True, text=True, timeout=120)
    return p.stdout + p.stderr


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, body, ctype, code=200):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            return self.send((VIEW / "index.html").read_bytes(), "text/html")
        if path == "/api/state":
            with state["lock"]:
                builds = dict(state["builds"])
            return self.send(json.dumps({
                "stamp": stamp(), "builds": builds,
                "svgs": sorted(p.name for p in (ROOT / "docs/img").glob("*.svg")),
                "glbs": sorted(str(p.relative_to(ROOT)) for p in (ROOT / "assets/models").rglob("*.glb"))}), "application/json")
        if path == "/api/sim":
            return self.send(sim_text(), "text/plain; charset=utf-8")
        rel = path.lstrip("/")
        f = (ROOT / rel).resolve()
        if rel.startswith(SERVED) and f.suffix in SERVED_EXT and ROOT in f.parents and f.is_file():
            return self.send(f.read_bytes(), mimetypes.guess_type(f.name)[0] or "application/octet-stream")
        self.send("not found", "text/plain", 404)


if __name__ == "__main__":
    threading.Thread(target=watcher, daemon=True).start()
    print(f"Sky Bullet dashboard: http://127.0.0.1:{PORT}  (Ctrl+C to stop)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
