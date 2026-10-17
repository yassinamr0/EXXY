"""Build the EXXY terrace in Blender and render it with Cycles (path tracing).

Usage (from the repo root, after `python blender/fetch_assets.py`):
    python blender/terrace.py --out renders/still.png             # final still
    python blender/terrace.py --out renders/test.png --preview    # fast low-res check
    python blender/terrace.py --save renders/terrace.blend        # also keep the .blend

Coordinates: metres, Z up. The visitor enters at -Y and looks towards +Y,
where the far wall frames the sea.
"""
import argparse
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "models")]

import bpy  # noqa: E402  (must come before bmesh)
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

import ex_dt_01  # noqa: E402
import lib  # noqa: E402
import lines  # noqa: E402

ASSETS = os.path.join(HERE, "assets")

# ------------------------------------------------------------------ layout
HW = 3.5            # half width of the terrace
H = 3.4             # wall height
ENTRANCE = -10.5    # floor edge behind the camera
FAR = 9.0           # inner face of the far wall
OPEN_W, OPEN_H = 3.2, 2.7
BALCONY = 2.5       # floor beyond the far wall
SUN_FROM = Vector((-7, 9, 4.0))    # low sun: ahead and to the left
SUN_COLOR = (1.0, 0.66, 0.40)
CAMERA = {"location": (0, -9.8, 1.5), "target": (0, 9, 1.35)}

SETS = [  # (x, y) of each table, table colour, chair colour
    ((-1.85, -3.2), "#ece8e1", "#d9ccb4"),
    ((1.85, 2.6), "#3d4043", "#6f7a58"),
]


# ------------------------------------------------------------------ materials

def image_node(nodes, path, colorspace, projection="BOX"):
    node = nodes.new("ShaderNodeTexImage")
    node.image = bpy.data.images.load(path, check_existing=True)
    node.image.colorspace_settings.name = colorspace
    node.projection = projection
    node.projection_blend = 0.25
    return node


def textured(name, tex_id, scale, tint=None, rough_mult=1.0, saturation=1.0, value=1.0):
    """PBR material using object coordinates, so boxes need no UVs."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes["Principled BSDF"]
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (scale, scale, scale)
    links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    base = os.path.join(ASSETS, "textures", tex_id)

    diff = image_node(nodes, os.path.join(base, "diff.jpg"), "sRGB")
    links.new(mapping.outputs["Vector"], diff.inputs["Vector"])
    color_out = diff.outputs["Color"]
    if saturation != 1.0 or value != 1.0:
        hsv = nodes.new("ShaderNodeHueSaturation")
        hsv.inputs["Saturation"].default_value = saturation
        hsv.inputs["Value"].default_value = value
        links.new(color_out, hsv.inputs["Color"])
        color_out = hsv.outputs["Color"]
    if tint:
        mix = nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        mix.inputs["B"].default_value = lib.hex_to_linear(tint)
        links.new(color_out, mix.inputs["A"])
        color_out = mix.outputs["Result"]
    links.new(color_out, bsdf.inputs["Base Color"])

    rough = image_node(nodes, os.path.join(base, "rough.jpg"), "Non-Color")
    links.new(mapping.outputs["Vector"], rough.inputs["Vector"])
    rmul = nodes.new("ShaderNodeMath")
    rmul.operation = "MULTIPLY"
    rmul.inputs[1].default_value = rough_mult
    links.new(rough.outputs["Color"], rmul.inputs[0])
    links.new(rmul.outputs["Value"], bsdf.inputs["Roughness"])

    nor = image_node(nodes, os.path.join(base, "nor.jpg"), "Non-Color")
    links.new(mapping.outputs["Vector"], nor.inputs["Vector"])
    nmap = nodes.new("ShaderNodeNormalMap")
    nmap.inputs["Strength"].default_value = 0.6
    links.new(nor.outputs["Color"], nmap.inputs["Color"])
    links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def sea_material():
    mat = bpy.data.materials.new("Sea")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = lib.hex_to_linear("#0f3346")
    bsdf.inputs["Roughness"].default_value = 0.06
    bsdf.inputs["IOR"].default_value = 1.33
    # gentle ripples so the sun leaves a glittering path on the water
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.6
    noise.inputs["Detail"].default_value = 8
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1, 4, 1)
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def wood_material():
    """Pale limed timber for the pergola: warmer than plaster, still quiet."""
    mat = bpy.data.materials.new("Pergola timber")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 40
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = lib.hex_to_linear("#cfc0aa")
    ramp.color_ramp.elements[1].color = lib.hex_to_linear("#ddd0bd")
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.8
    return mat


# ------------------------------------------------------------------ geometry

def boxes_object(name, boxes, material, bevel=0.012):
    bm = bmesh.new()
    for center, size in boxes:
        lib.box(bm, center, size)
    obj = lib.new_object(name, bm, material, smooth_angle=30)
    if bevel:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
        mod.harden_normals = True
    return obj


def build_architecture():
    stucco = textured("Stucco", "white_stucco", 0.6, tint="#fbf4ea", rough_mult=1.1)
    paving = textured("Paving", "patio_tiles", 0.6, tint="#f8ecdb", saturation=0.5, value=1.3)
    length = FAR - ENTRANCE
    mid_y = (FAR + ENTRANCE) / 2

    # floor, running out onto the balcony
    bpy.ops.mesh.primitive_plane_add(size=1)
    floor = bpy.context.active_object
    floor.name = "Floor"
    floor.scale = (HW * 2 + 6, length + BALCONY, 1)
    floor.location = (0, (ENTRANCE + FAR + BALCONY) / 2, 0)
    bpy.ops.object.transform_apply(scale=True, location=True)
    floor.data.materials.append(paving)

    piers = []
    y = ENTRANCE + 1.2
    while y < FAR:
        # piers stop under the beam so no faces overlap (that renders black)
        piers.append(((-HW - 0.22, y, (H - 0.5) / 2), (0.45, 0.5, H - 0.5)))
        y += 2.6
    piers.append(((-HW - 0.22, mid_y, H - 0.25), (0.45, length, 0.5)))
    boxes_object("Colonnade", piers, stucco)

    boxes_object("Right wall", [((HW + 0.15, mid_y, H / 2), (0.3, length, H))], stucco)

    side = (HW * 2 - OPEN_W) / 2
    boxes_object("Far wall", [
        ((-HW + side / 2, FAR + 0.15, H / 2), (side, 0.3, H)),
        ((HW - side / 2, FAR + 0.15, H / 2), (side, 0.3, H)),
        ((0, FAR + 0.15, (H + OPEN_H) / 2), (OPEN_W, 0.3, H - OPEN_H)),
    ], stucco)

    slats = []
    y = ENTRANCE + 1.5
    while y < FAR - 0.3:
        slats.append(((0, y, H + 0.07), (HW * 2 + 0.6, 0.05, 0.1)))
        y += 0.7
    boxes_object("Pergola", slats, wood_material(), bevel=0.006)

    boxes_object("Balcony wall", [((0, FAR + BALCONY - 0.12, 0.2), (HW * 2 + 6, 0.25, 0.4))], stucco)

    bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, -3))
    sea = bpy.context.active_object
    sea.name = "Sea"
    sea.data.materials.append(sea_material())


def place(obj, location, rot_z=0.0):
    obj.location = location
    obj.rotation_euler = (0, 0, rot_z)
    return obj


def build_furniture():
    for (x, y), table_color, chair_color in SETS:
        table = ex_dt_01.build(table_color)
        bevel = table.modifiers.new("Bevel", "BEVEL")
        bevel.width = 0.003
        bevel.segments = 2
        bevel.limit_method = "ANGLE"
        place(table, (x, y, 0), math.pi / 2)
        chair = lines.build(chair_color)
        first = True
        for side in (-1, 1):
            for dy in (-0.45, 0.45):
                c = chair if first else chair.copy()
                if not first:
                    bpy.context.collection.objects.link(c)
                first = False
                # chairs face -Y; turn each towards the table
                place(c, (x + side * 0.72, y + dy, 0), -side * math.pi / 2)


def import_model(asset_id, height, location, rot_z=0.0):
    """Import a Poly Haven glTF and scale it to a real-world height."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ASSETS, "models", asset_id, f"{asset_id}.gltf"))
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(asset_id, None)
    bpy.context.collection.objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in new if o.type == "MESH" for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    s = height / (hi.z - lo.z)
    for o in new:
        if o.parent is root:
            o.location -= Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    root.scale = (s, s, s)
    root.location = location
    root.rotation_euler = (0, 0, rot_z)
    return root


def build_planting():
    # olive-like trees in terracotta pots, against the warm right wall
    for (x, y, rz) in [(2.75, -7.0, 0.4), (2.75, 6.2, 2.1), (-2.8, 7.3, 1.2)]:
        import_model("planter_pot_clay", 0.62, (x, y, 0), rz)
        import_model("island_tree_01", 2.6, (x, y, 0.45), rz)
    import_model("potted_plant_02", 0.9, (-1.0, FAR - 0.45, 0), 0.5)
    import_model("ceramic_vase_03", 0.75, (1.1, FAR - 0.4, 0))
    import_model("ceramic_vase_01", 0.32, (SETS[0][0][0], SETS[0][0][1] + 0.2, 0.75))


# ------------------------------------------------------------------ light + camera

def hdri_sun_u(path):
    """Horizontal position (0-1) of the brightest point in an equirectangular HDRI."""
    img = bpy.data.images.load(path, check_existing=True)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    lum = px.reshape(h, w, 4)[..., :3].sum(axis=2)
    _, col = np.unravel_index(np.argmax(lum), lum.shape)
    return col / w


def build_lighting():
    world = bpy.data.worlds.new("Golden hour")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    path = os.path.join(ASSETS, "hdri", "umhlanga_sunrise.hdr")
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(path, check_existing=True)
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    # Turn the sky so its sun sits where our sun lamp is. A point at image
    # position u appears at azimuth A when rotation = 2*pi*u + 99deg - A
    # (measured by rendering the sky at known rotations).
    want = math.atan2(SUN_FROM.y, SUN_FROM.x)
    mapping.inputs["Rotation"].default_value[2] = 2 * math.pi * hdri_sun_u(path) + math.radians(99) - want
    nt.links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], env.inputs["Vector"])
    bg = nt.nodes["Background"]
    bg.inputs["Strength"].default_value = 0.55
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])

    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 4.2
    sun_data.color = SUN_COLOR
    sun_data.angle = math.radians(1.2)
    sun = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler = SUN_FROM.to_track_quat("Z", "Y").to_euler()


def build_camera(portrait=True):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.lens = 40 if portrait else 24
    cam_data.dof.use_dof = True
    cam_data.dof.focus_distance = 9.0
    cam_data.dof.aperture_fstop = 5.6
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = CAMERA["location"]
    direction = Vector(CAMERA["target"]) - Vector(CAMERA["location"])
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


def setup_render(portrait, preview, samples):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.adaptive_threshold = 0.02
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 8
    scene.cycles.diffuse_bounces = 4
    scene.cycles.glossy_bounces = 3
    scene.cycles.transparent_max_bounces = 16
    scene.cycles.caustics_reflective = scene.cycles.caustics_refractive = False
    scene.cycles.sample_clamp_indirect = 8
    w, h = (1080, 1920) if portrait else (1920, 1080)
    scene.render.resolution_x, scene.render.resolution_y = w, h
    scene.render.resolution_percentage = 40 if preview else 100
    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    scene.view_settings.exposure = 0.2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "renders", "still.png"))
    ap.add_argument("--landscape", action="store_true", help="desktop framing (default: phone)")
    ap.add_argument("--preview", action="store_true", help="40%% resolution, few samples")
    ap.add_argument("--samples", type=int, default=96)
    ap.add_argument("--save", help="also save the .blend here")
    args = ap.parse_args()

    lib.reset_scene()
    build_architecture()
    build_furniture()
    build_planting()
    build_lighting()
    build_camera(portrait=not args.landscape)
    setup_render(not args.landscape, args.preview, 16 if args.preview else args.samples)

    if args.save:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.save))
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("saved", out)


if __name__ == "__main__":
    main()
