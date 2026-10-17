"""Shared helpers for building EXXY furniture in Blender from code.

Units are metres. Blender is Z-up; furniture faces -Y (towards the viewer).
The GLB exporter converts to the Y-up convention used by three.js.
"""
import math

import bmesh
import bpy
from mathutils import Vector


# ---------------------------------------------------------------- scene

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def powder_coat(name, hex_color, roughness=0.5):
    """Powder coating is paint, not bare metal: non-metallic, satin finish."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = hex_to_linear(hex_color)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def hex_to_linear(hex_color):
    h = hex_color.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, 1.0)


def new_object(name, bm, material, smooth_angle=None):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    if smooth_angle is not None:
        mesh.shade_smooth()
        mesh.set_sharp_from_angle(angle=math.radians(smooth_angle))
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def join(objects, name):
    """Merge parts into one object so each product is a single, light mesh."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    obj.data.name = name
    return obj


# ---------------------------------------------------------------- shapes

def box(bm, center, size):
    """Axis-aligned box. size = (x, y, z) full dimensions."""
    ret = bmesh.ops.create_cube(bm, size=1.0)
    verts = ret["verts"]
    bmesh.ops.scale(bm, vec=Vector(size), verts=verts)
    bmesh.ops.translate(bm, vec=Vector(center), verts=verts)


def rounded_path(corners, radius, segments=8):
    """Polyline through `corners`, with each inner corner replaced by an arc.

    This mimics bent tube or bent flat bar: straight runs joined by bends.
    `radius` can be a single number or a list (one per inner corner).
    """
    pts = [Vector(c) for c in corners]
    radii = radius if isinstance(radius, (list, tuple)) else [radius] * (len(pts) - 2)
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        d0, d1 = (p0 - p1).normalized(), (p2 - p1).normalized()
        angle = d0.angle(d1)
        r = radii[i - 1]
        if r <= 0 or angle > math.pi - 1e-3:
            out.append(p1)
            continue
        # distance from the corner to where the arc touches each straight run
        t = r / math.tan(angle / 2)
        t = min(t, (p0 - p1).length * 0.49, (p2 - p1).length * 0.49)
        a, b = p1 + d0 * t, p1 + d1 * t
        for s in range(segments + 1):
            u = s / segments
            # quadratic Bezier with control point at the corner: a smooth bend
            out.append((1 - u) ** 2 * a + 2 * (1 - u) * u * p1 + u ** 2 * b)
    out.append(pts[-1])
    return out


def circle_profile(radius, segments=12):
    return [(radius * math.cos(2 * math.pi * i / segments),
             radius * math.sin(2 * math.pi * i / segments)) for i in range(segments)]


def rect_profile(width, thickness):
    w, t = width / 2, thickness / 2
    return [(-w, -t), (w, -t), (w, t), (-w, t)]


def sweep(bm, path, plane_normal, profile, caps=True):
    """Sweep a 2D profile along a path lying in a plane.

    Profile x runs along `plane_normal` (e.g. the width of a flat bar),
    profile y runs perpendicular to the path inside the plane.
    """
    n = Vector(plane_normal).normalized()
    path = [Vector(p) for p in path]
    rings = []
    for i, p in enumerate(path):
        if i == 0:
            t = path[1] - path[0]
        elif i == len(path) - 1:
            t = path[-1] - path[-2]
        else:
            t = (path[i + 1] - path[i - 1])
        t.normalize()
        side = (n - t * n.dot(t)).normalized()
        up = t.cross(side)
        rings.append([bm.verts.new(p + side * x + up * y) for x, y in profile])
    k = len(profile)
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(k):
            bm.faces.new((r0[j], r0[(j + 1) % k], r1[(j + 1) % k], r1[j]))
    if caps:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])


# ---------------------------------------------------------------- export

def export_glb(obj, filepath):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
    )


def stats(obj):
    me = obj.data
    return f"{len(me.vertices)} verts, {len(me.polygons)} faces"
