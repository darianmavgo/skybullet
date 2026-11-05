#!/usr/bin/env python3
"""Search and download Poly Pizza models (.glb) into the Godot project.

Setup:  put POLYPIZZA_API_KEY=... in .env at the repo root (git-ignored), or export it.
        Free key: poly.pizza account settings.
Usage:
  tools/polypizza.py search glider [--limit 10] [--raw]
  tools/polypizza.py get <model-id> [--name glider_basic] [--dest DIR]

Downloads the .glb and logs source + license to ASSETS_LICENSES.md.
Response field names are matched case-insensitively and are based on third-party
docs; use --raw to see the real JSON if a field shows up as '?'.
"""
import argparse, json, os, sys, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

API = "https://api.poly.pizza/v1"
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DEST = ROOT / "assets" / "models" / "polypizza"
LOG = ROOT / "ASSETS_LICENSES.md"


def load_key():
    """API key from the environment, else from KEY=value lines in <repo>/.env."""
    key = os.environ.get("POLYPIZZA_API_KEY")
    env = ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if line.startswith("POLYPIZZA_API_KEY="):
                key = line.split("=", 1)[1].strip().strip("'\"")
    return key


def call(url, headers=None):
    key = load_key()
    h = {"User-Agent": "skybullet-asset-tool"}
    if headers is not None:
        h.update(headers)
    else:
        if not key:
            sys.exit("No API key. Put POLYPIZZA_API_KEY=... in .env at the repo root (poly.pizza account settings).")
        h["X-Auth-Token"] = key
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30) as r:
        return r.read()


def field(d, *names, default="?"):
    low = {k.lower(): v for k, v in d.items()}
    for n in names:
        if n.lower() in low and low[n.lower()] not in (None, ""):
            return low[n.lower()]
    return default


def creator(d):
    c = field(d, "creator", "author", default={})
    return field(c, "username", "name") if isinstance(c, dict) else c


def results(data):
    if isinstance(data, list):
        return data
    return field(data, "results", "models", default=[])


def cmd_search(a):
    q = urllib.parse.quote(a.query)
    data = json.loads(call(f"{API}/search/{q}?Limit={a.limit}"))
    if a.raw:
        print(json.dumps(data, indent=2)); return
    for m in results(data):
        print(f"{field(m,'ID'):<24} {str(field(m,'Title')):<32} "
              f"{str(field(m,'Licence','License')):<8} by {creator(m)}  tris={field(m,'Tri Count','TriCount')}")


def cmd_get(a):
    m = json.loads(call(f"{API}/model/{a.id}"))
    if a.raw:
        print(json.dumps(m, indent=2)); return
    url = field(m, "Download", "GLB", "DownloadUrl", default=None)
    if not url:
        sys.exit("No download URL found; rerun with --raw to inspect the response.")
    title = str(field(m, "Title"))
    name = a.name or "".join(c if c.isalnum() else "_" for c in title.lower()).strip("_")
    dest = Path(a.dest) if a.dest else DEFAULT_DEST
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{name}.glb"
    out.write_bytes(call(url, headers={}))  # CDN link, no auth header
    lic = field(m, "Licence", "License")
    new = not LOG.exists()
    with LOG.open("a") as f:
        if new:
            f.write("# Asset licenses\n\n| File | Title | Creator | License | Source | Added |\n|---|---|---|---|---|---|\n")
        f.write(f"| {out.relative_to(ROOT)} | {title} | {creator(m)} | {lic} | https://poly.pizza/m/{a.id} | {date.today()} |\n")
    print(f"Saved {out} ({lic}, by {creator(m)}). Logged in {LOG.name}.")


p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
s = p.add_subparsers(dest="cmd", required=True)
x = s.add_parser("search"); x.add_argument("query"); x.add_argument("--limit", type=int, default=10); x.add_argument("--raw", action="store_true"); x.set_defaults(f=cmd_search)
x = s.add_parser("get"); x.add_argument("id"); x.add_argument("--name"); x.add_argument("--dest"); x.add_argument("--raw", action="store_true"); x.set_defaults(f=cmd_get)
a = p.parse_args(); a.f(a)
