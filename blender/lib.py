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


# ---------------------------------------------------------------- more shapes

def cylinder(bm, center, radius, height, segments=32):
    """Upright cylinder; `center` is the middle of its base."""
    ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=segments,
                                radius1=radius, radius2=radius, depth=height)
    bmesh.ops.translate(bm, vec=Vector(center) + Vector((0, 0, height / 2)), verts=ret["verts"])


def slab(bm, outline, z0, z1):
    """Flat solid from a 2D outline (list of (x, y), counter-clockwise)."""
    bottom = [bm.verts.new((x, y, z0)) for x, y in outline]
    top = [bm.verts.new((x, y, z1)) for x, y in outline]
    bm.faces.new(list(reversed(bottom)))
    bm.faces.new(top)
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bottom[i], bottom[j], top[j], top[i]))


def stadium(length, width, segments=16):
    """Outline of a rectangle with fully rounded ends (a running-track shape)."""
    r = width / 2
    cx = length / 2 - r
    pts = []
    for s in range(segments + 1):
        a = -math.pi / 2 + math.pi * s / segments
        pts.append((cx + r * math.cos(a), r * math.sin(a)))
    for s in range(segments + 1):
        a = math.pi / 2 + math.pi * s / segments
        pts.append((-cx + r * math.cos(a), r * math.sin(a)))
    return pts


def ellipse(rx, ry, segments=48):
    return [(rx * math.cos(2 * math.pi * i / segments), ry * math.sin(2 * math.pi * i / segments))
            for i in range(segments)]


def circle_path(center, radius, segments=48):
    """Closed horizontal ring path (first point repeated at the end)."""
    cx, cy, cz = center
    return [(cx + radius * math.cos(2 * math.pi * i / segments),
             cy + radius * math.sin(2 * math.pi * i / segments), cz) for i in range(segments + 1)]


def cushion(name, size, location, material, softness=0.35, puff=0.12, rotation=(0, 0, 0)):
    """Upholstered cushion: a box with soft rounded edges and slightly domed faces."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=3, use_grid_fill=True)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    obj = new_object(name, bm, material)
    obj.location = location
    obj.rotation_euler = rotation
    bevel = obj.modifiers.new("Soft edges", "BEVEL")
    bevel.width = min(size) * softness
    bevel.segments = 5
    bevel.limit_method = "NONE"
    cast = obj.modifiers.new("Puff", "CAST")
    cast.factor = puff
    cast.use_z = cast.use_x = cast.use_y = True
    sub = obj.modifiers.new("Smooth", "SUBSURF")
    sub.levels = sub.render_levels = 1
    obj.data.shade_smooth()
    return obj


def round_cushion(name, rx, ry, thickness, location, material):
    bm = bmesh.new()
    slab(bm, ellipse(rx, ry, 64), -thickness / 2, thickness / 2)
    obj = new_object(name, bm, material)
    obj.location = location
    bevel = obj.modifiers.new("Soft edges", "BEVEL")
    bevel.width = thickness * 0.45
    bevel.segments = 6
    bevel.limit_method = "NONE"
    obj.data.shade_smooth()
    return obj


def apply_modifiers(obj):
    bpy.context.view_layer.objects.active = obj
    for m in list(obj.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def assemble(name, parts):
    """Apply each part's modifiers and join them into one object."""
    for p in parts:
        apply_modifiers(p)
    return join(parts, name)


# ---------------------------------------------------------------- more materials

def fabric(name, hex_color, weave_scale=900):
    """Outdoor upholstery: matte, soft sheen at grazing angles, fine weave."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = hex_to_linear(hex_color)
    bsdf.inputs["Roughness"].default_value = 0.85
    bsdf.inputs["Sheen Weight"].default_value = 0.6
    bsdf.inputs["Sheen Roughness"].default_value = 0.4
    weave = nt.nodes.new("ShaderNodeTexWave")
    weave.inputs["Scale"].default_value = weave_scale
    weave.inputs["Distortion"].default_value = 1.5
    coord = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(coord.outputs["Object"], weave.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.15
    nt.links.new(weave.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def teak(name="Teak"):
    """Oiled teak with grain running along X."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (0.4, 12, 12)
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3
    noise.inputs["Detail"].default_value = 10
    noise.inputs["Distortion"].default_value = 0.6
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hex_to_linear("#5e3a1f")
    ramp.color_ramp.elements[1].color = hex_to_linear("#9a6a43")
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.45
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.05
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat
