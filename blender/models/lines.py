"""LINES (EX-CH-14) — slatted steel / aluminium chair, side-chair version.

No dimensions are listed on the site; these are typical for this design:
about 55 W x 52 D x 80 H cm, seat height 45 cm.
Reference photos: exxyshop.com/products/ex-ch-14
Structure: round tube frame (back legs run up into the back), front legs
bend back into the seat sides, flat bars run from the top of the back
down and forward over the seat.
"""
import bmesh

import lib

HALF_W = 0.25        # tube centre line, half width
SEAT_Z = 0.45
TOP_Z = 0.79
TUBE_R = 0.011       # 22 mm tube
SLATS = 7
SLAT_W = 0.034
SLAT_T = 0.005
SPLAY = 0.012        # feet sit slightly wider than the seat


def build(color="#5d6a3d"):
    mat = lib.powder_coat("LINES powder coat", color)
    bm = bmesh.new()
    tube = lib.circle_profile(TUBE_R, 12)
    w = HALF_W

    # back legs + back frame: one continuous bent tube
    back = lib.rounded_path([
        (-w - SPLAY, 0.245, 0.0), (-w, 0.205, SEAT_Z), (-w, 0.27, TOP_Z),
        (w, 0.27, TOP_Z), (w, 0.205, SEAT_Z), (w + SPLAY, 0.245, 0.0),
    ], radius=[0.03, 0.06, 0.06, 0.03], segments=8)
    lib.sweep(bm, back, (0, 1, 0.3), tube)

    # front legs bend backwards into the seat side rails
    for sx in (-1, 1):
        side = lib.rounded_path([
            (sx * (w + SPLAY), -0.24, 0.0), (sx * w, -0.205, SEAT_Z), (sx * w, 0.205, SEAT_Z),
        ], radius=0.05, segments=8)
        lib.sweep(bm, side, (1, 0, 0), tube)

    # front rail under the seat edge
    lib.sweep(bm, [(-w, -0.205, SEAT_Z - 0.02), (w, -0.205, SEAT_Z - 0.02)], (0, 1, 0), tube)

    # flat bars: down the back, bend, forward over the seat, curl over the front
    bar = lib.rect_profile(SLAT_W, SLAT_T)
    inner = 2 * w - 2 * TUBE_R - SLAT_W - 0.012
    pitch = inner / (SLATS - 1)
    for i in range(SLATS):
        x = -inner / 2 + i * pitch
        z_seat = SEAT_Z + TUBE_R + SLAT_T / 2
        path = lib.rounded_path([
            (x, 0.268, TOP_Z - 0.005), (x, 0.198, z_seat),
            (x, -0.200, z_seat), (x, -0.222, SEAT_Z - 0.03),
        ], radius=[0.07, 0.02], segments=8)
        lib.sweep(bm, path, (1, 0, 0), bar)

    return lib.new_object("LINES", bm, mat, smooth_angle=40)
