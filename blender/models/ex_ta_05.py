"""EX-TA-05 — round bistro table on hairpin legs.

Listed: diameter 80 cm, height 75 cm, metal, powder electrostatic coated.
Reference photos: exxyshop.com/products/ex-ta-05
Structure: thin round top, three hairpin legs (one bent rod each), a ring
tying the legs together just above half height.
"""
import math

import bmesh

import lib

R_TOP = 0.40
HEIGHT = 0.75
TOP_T = 0.014
ROD = 0.0065


def build(color="#2f3134"):
    mat = lib.powder_coat("EX-TA-05 powder coat", color)
    bm = bmesh.new()
    lib.slab(bm, lib.ellipse(R_TOP, R_TOP, 64), HEIGHT - TOP_T, HEIGHT)
    rod = lib.circle_profile(ROD, 10)
    z_top = HEIGHT - TOP_T
    for k in range(3):
        a = math.pi / 2 + k * 2 * math.pi / 3
        # each leg: one rod bent into a narrow U, both ends fixed under the top
        top_a = (0.14 * math.cos(a - 0.95), 0.14 * math.sin(a - 0.95), z_top)
        foot = (0.37 * math.cos(a), 0.37 * math.sin(a), 0.0)
        top_b = (0.14 * math.cos(a + 0.95), 0.14 * math.sin(a + 0.95), z_top)
        pts = lib.rounded_path([top_a, foot, top_b], radius=0.035, segments=10)
        lib.sweep(bm, pts, (math.cos(a), math.sin(a), 0), rod)
    # tie ring where the legs pass through it
    z_ring = 0.42
    lib.sweep(bm, lib.circle_path((0, 0, z_ring), 0.235), (0, 0, 1), rod, caps=False)
    return lib.new_object("EX-TA-05", bm, mat, smooth_angle=40)
