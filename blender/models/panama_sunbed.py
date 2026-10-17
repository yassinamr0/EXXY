"""Panama Sunbed — round daybed with adjustable backrest.

Listed: 150 x 200 cm, height 35 cm, aluminium, powder electrostatic coated.
Reference photos: exxyshop.com/products/panama-sunbed
Structure: oval cushion on a flat platform, a tube ring running around it
lower down, short legs, a tilted backrest with its own cushion, two pillows.
"""
import math

import bmesh

import lib

RX, RY = 1.0, 0.75        # half length / half width of the cushion
PLATFORM_Z = 0.20
CUSHION_T = 0.12


def build(color="#a23a2c", fabric_color="#d9ccb5"):
    metal = lib.powder_coat("Panama powder coat", color)
    cloth = lib.fabric("Panama cushion", fabric_color)
    bm = bmesh.new()
    lib.slab(bm, lib.ellipse(RX - 0.02, RY - 0.02, 64), PLATFORM_Z - 0.02, PLATFORM_Z)
    ring = [(1.06 * RX * math.cos(a), 1.06 * RY * math.sin(a), 0.12)
            for a in [2 * math.pi * i / 64 for i in range(65)]]
    tube = lib.circle_profile(0.012, 12)
    lib.sweep(bm, ring, (0, 0, 1), tube, caps=False)
    for a in (0.6, math.pi - 0.6, math.pi + 0.6, -0.6):
        x, y = 1.06 * RX * math.cos(a), 1.06 * RY * math.sin(a)
        lib.cylinder(bm, (x, y, 0), 0.014, 0.12)
        lib.cylinder(bm, (x * 0.8, y * 0.8, 0.12), 0.012, PLATFORM_Z - 0.14)
        lib.sweep(bm, [(x, y, 0.12), (x * 0.8, y * 0.8, 0.12)], (0, 0, 1), tube)
    # backrest: frame bars and cushion share one tilted axis rising from the -X end
    b = math.radians(38)
    d = (-math.cos(b), 0, math.sin(b))          # up the backrest
    n = (math.sin(b), 0, math.cos(b))           # out of the backrest, towards the sitter
    base = (-0.42, 0, PLATFORM_Z + 0.02)

    def at(along, out, y=0.0):
        return (base[0] + d[0] * along + n[0] * out, y, base[2] + d[2] * along + n[2] * out)

    for sy in (-1, 1):
        lib.sweep(bm, [at(0, 0, sy * 0.3), at(0.7, 0, sy * 0.3)], (0, 1, 0), tube)
    frame = lib.new_object("Panama frame", bm, metal, smooth_angle=40)

    z_top = PLATFORM_Z + CUSHION_T / 2
    parts = [frame, lib.round_cushion("Panama seat", RX - 0.03, RY - 0.03, CUSHION_T, (0, 0, z_top), cloth)]
    parts.append(lib.cushion("Panama back", (0.70, 0.70, 0.11), at(0.4, 0.07), cloth,
                             softness=0.45, puff=0.2, rotation=(0, b, 0)))
    for y, rz in ((-0.17, 0.12), (0.19, -0.1)):
        parts.append(lib.cushion("Panama pillow", (0.34, 0.40, 0.13), at(0.36, 0.2, y), cloth,
                                 softness=0.5, puff=0.5, rotation=(0, b - 0.15, rz)))
    return lib.assemble("Panama Sunbed", parts)
