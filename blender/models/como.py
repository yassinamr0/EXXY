"""COMO lounge set — tube-frame sofa, armchair and coffee table with cushions.

Listed: 3-seater sofa 217 x 73 x 80H, 2-seater 160 x 73 x 80H,
armchair 75 x 73 x 80H, table 100 x 60 x 38H cm; aluminium or metal,
powder electrostatic coated.
Reference photos: exxyshop.com/products/lounge-set2
Structure: each end is one closed tube loop (front leg, armrest, back leg,
floor runner); rails tie the ends together under the seat and behind the back.
"""
import bmesh

import lib

DEPTH = 0.73
ARM_Z = 0.60
SEAT_Z = 0.36
TUBE_R = 0.016


def _frame(bm, width):
    tube = lib.circle_profile(TUBE_R, 14)
    hw, hd = width / 2 - TUBE_R, DEPTH / 2 - TUBE_R
    for sx in (-1, 1):
        x = sx * hw
        loop = lib.rounded_path([
            (x, -hd + 0.05, 0.0), (x, -hd, ARM_Z), (x, hd, ARM_Z), (x, hd, 0.0), (x, -hd + 0.05, 0.0),
        ], radius=0.06, segments=8)
        lib.sweep(bm, loop, (1, 0, 0), tube, caps=False)
    for y, z in ((-hd, SEAT_Z - 0.05), (hd, SEAT_Z - 0.05), (hd, ARM_Z)):
        lib.sweep(bm, [(-hw, y, z), (hw, y, z)], (0, 1, 0), tube)
    # seat deck that the cushions rest on
    lib.box(bm, (0, 0, SEAT_Z - 0.04), (width - 0.06, DEPTH - 0.06, 0.02))


def _seating(name, seats, color="#ffffff", fabric_color="#cfcac2"):
    width = {1: 0.75, 2: 1.60, 3: 2.17}[seats]
    metal = lib.powder_coat(f"COMO {name} frame", color)
    cloth = lib.fabric(f"COMO {name} cushions", fabric_color)
    bm = bmesh.new()
    _frame(bm, width)
    parts = [lib.new_object(f"COMO {name} frame", bm, metal, smooth_angle=40)]
    inner = width - 0.08
    cw = inner / seats
    for i in range(seats):
        x = -inner / 2 + cw * (i + 0.5)
        parts.append(lib.cushion("seat", (cw - 0.01, DEPTH - 0.1, 0.15), (x, -0.02, SEAT_Z + 0.06), cloth))
        parts.append(lib.cushion("back", (cw - 0.02, 0.17, 0.46), (x, DEPTH / 2 - 0.12, SEAT_Z + 0.33),
                                 cloth, rotation=(-0.18, 0, 0)))
    # loose side pillows leaning on the armrests
    for sx in (-1, 1):
        parts.append(lib.cushion("pillow", (0.14, 0.42, 0.40), (sx * (inner / 2 - 0.1), 0.0, SEAT_Z + 0.32),
                                 cloth, softness=0.45, puff=0.25, rotation=(0, sx * 0.25, 0)))
    return lib.assemble(f"COMO {name}", parts)


def build_sofa(color="#ffffff", fabric_color="#cfcac2"):
    return _seating("sofa", 3, color, fabric_color)


def build_armchair(color="#ffffff", fabric_color="#cfcac2"):
    return _seating("armchair", 1, color, fabric_color)


def build_table(color="#ffffff"):
    mat = lib.powder_coat("COMO table", color)
    bm = bmesh.new()
    tube = lib.circle_profile(TUBE_R, 14)
    for sx in (-1, 1):
        x = sx * 0.47
        loop = lib.rounded_path([(x, -0.27, 0.0), (x, -0.27, 0.36), (x, 0.27, 0.36), (x, 0.27, 0.0), (x, -0.27, 0.0)],
                                radius=0.05, segments=8)
        lib.sweep(bm, loop, (1, 0, 0), tube, caps=False)
    lib.box(bm, (0, 0, 0.37), (1.0, 0.6, 0.02))
    return lib.new_object("COMO table", bm, mat, smooth_angle=40)


def build(color="#ffffff"):
    return build_sofa(color)
