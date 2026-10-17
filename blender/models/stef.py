"""STEF — wire chair with a round seat and oval rod back.

No dimensions listed; typical: 50 W x 52 D x 80 H cm, seat height 45 cm.
Reference photos: exxyshop.com/products/stef
"""
import math

import bmesh

import lib

SEAT_Z = 0.45
SEAT_R = 0.22


def build(color="#a7b5a0"):
    mat = lib.powder_coat("STEF powder coat", color)
    bm = bmesh.new()
    tube = lib.circle_profile(0.009, 12)
    rod = lib.circle_profile(0.0035, 8)
    # round seat: thin plate with a rolled rim
    lib.slab(bm, lib.ellipse(SEAT_R, SEAT_R, 48), SEAT_Z - 0.004, SEAT_Z)
    lib.sweep(bm, lib.circle_path((0, 0, SEAT_Z - 0.004), SEAT_R), (0, 0, 1), tube, caps=False)
    # four legs, slightly splayed
    for ax, ay in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        top = (ax * 0.16, ay * 0.15, SEAT_Z - 0.01)
        foot = (ax * 0.2, ay * 0.21, 0.0)
        lib.sweep(bm, [foot, top], (1, 0, 0), tube)
    # back legs continue up into an oval back frame, leaning back
    lean = math.radians(10)
    cx, cz = 0.0, SEAT_Z + 0.13
    rx, rz = 0.2, 0.11
    ring = []
    for i in range(49):
        a = 2 * math.pi * i / 48
        x, z = rx * math.cos(a), rz * math.sin(a)
        ring.append((cx + x, 0.2 + (z + 0.2) * math.sin(lean), cz + 0.08 + z * math.cos(lean)))
    lib.sweep(bm, ring, (0, 1, 0), tube, caps=False)
    for sx in (-1, 1):
        lib.sweep(bm, [(sx * 0.16, 0.15, SEAT_Z - 0.01), (sx * 0.17, 0.2 + 0.06 * math.sin(lean), cz - 0.02)], (1, 0, 0), tube)
    # vertical rods filling the back
    for i in range(1, 14):
        x = -rx + 2 * rx * i / 14
        zr = rz * math.sqrt(max(0.0, 1 - (x / rx) ** 2))
        pts = []
        for z in (-zr, zr):
            pts.append((x, 0.2 + (z + 0.2) * math.sin(lean), cz + 0.08 + z * math.cos(lean)))
        lib.sweep(bm, pts, (1, 0, 0), rod)
    return lib.new_object("STEF", bm, mat, smooth_angle=40)
