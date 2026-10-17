"""Download the free (CC0) Poly Haven assets the terrace render uses.

Usage:  python blender/fetch_assets.py
Files land in blender/assets/ (git-ignored; re-download any time).
Poly Haven assets are CC0: free for commercial use, no attribution needed.
"""
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets")

TEXTURES = ["white_stucco", "patio_tiles"]
MODELS = ["island_tree_01", "planter_pot_clay", "potted_plant_02", "ceramic_vase_01", "ceramic_vase_03"]
HDRIS = ["umhlanga_sunrise"]
TEX_MAPS = {"Diffuse": "diff", "nor_gl": "nor", "Rough": "rough"}


def get(url, path):
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "exxy-terrace/1.0"})
    with urllib.request.urlopen(req) as r, open(path, "wb") as f:
        f.write(r.read())
    print("  ", os.path.relpath(path, HERE))


def files(asset_id):
    req = urllib.request.Request(f"https://api.polyhaven.com/files/{asset_id}",
                                 headers={"User-Agent": "exxy-terrace/1.0"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def main():
    for tid in TEXTURES:
        f = files(tid)
        for key, short in TEX_MAPS.items():
            url = f[key]["2k"]["jpg"]["url"]
            get(url, os.path.join(OUT, "textures", tid, f"{short}.jpg"))
    for mid in MODELS:
        g = files(mid)["gltf"]["1k"]["gltf"]
        base = os.path.join(OUT, "models", mid)
        get(g["url"], os.path.join(base, f"{mid}.gltf"))
        for rel, inc in g.get("include", {}).items():
            get(inc["url"], os.path.join(base, rel))
    for hid in HDRIS:
        get(files(hid)["hdri"]["4k"]["hdr"]["url"], os.path.join(OUT, "hdri", f"{hid}.hdr"))


if __name__ == "__main__":
    main()
