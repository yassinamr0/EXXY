"""Build EXXY furniture models, export GLB, and render a preview.

Usage (from the repo root):
    python blender/build.py ex_dt_01 lines --render previews/

Needs the `bpy` package (Blender as a Python module), Python 3.13:
    python3.13 -m venv .venv && .venv/bin/pip install bpy
"""
import argparse
import importlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "models")]

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import lib  # noqa: E402

OUT_DIR = os.path.join(HERE, "..", "web", "src", "models")


def render_preview(obj, filepath, yaw=-35, pitch=12, size=(900, 700)):
    """Studio-style render on white, roughly matching catalogue photos."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.view_settings.view_transform = "Standard"

    world = bpy.data.worlds.new("studio")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    scene.world = world

    # floor that only catches shadows, like a seamless photo backdrop
    bpy.ops.mesh.primitive_plane_add(size=20)
    floor = bpy.context.active_object
    floor.is_shadow_catcher = True
    scene.render.film_transparent = False

    bpy.ops.object.light_add(type="AREA", location=(-1.5, -2.0, 3.0))
    key = bpy.context.active_object
    key.data.energy = 400
    key.data.size = 3
    key.rotation_euler = (math.radians(35), 0, math.radians(-35))

    # frame the object from a 3/4 view
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    center = sum(corners, Vector()) / 8
    radius = max((c - center).length for c in corners)
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 70
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    dist = radius / math.tan(cam_data.angle / 2) * 1.05
    y, p = math.radians(yaw), math.radians(pitch)
    cam.location = center + Vector((math.sin(y) * math.cos(p),
                                    -math.cos(y) * math.cos(p),
                                    math.sin(p))) * dist
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam

    scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("models", nargs="+")
    ap.add_argument("--color", help="override powder-coat colour, e.g. #f2efe8")
    ap.add_argument("--render", metavar="DIR", help="also render a preview PNG here")
    ap.add_argument("--yaw", type=float, default=-35)
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    for name in args.models:
        lib.reset_scene()
        module = importlib.import_module(name)
        obj = module.build(args.color) if args.color else module.build()
        glb = os.path.join(OUT_DIR, f"{name}.glb")
        lib.export_glb(obj, glb)
        print(f"{name}: {lib.stats(obj)}, {os.path.getsize(glb) / 1024:.0f} KB -> {glb}")
        if args.render:
            os.makedirs(args.render, exist_ok=True)
            render_preview(obj, os.path.abspath(os.path.join(args.render, f"{name}.png")), yaw=args.yaw)


if __name__ == "__main__":
    main()
