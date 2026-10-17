"""EX-DT-01 — slatted aluminium dining table.

Listed sizes: 180 x 90 x 75H cm and 210 x 90 x 75H cm.
Reference photos: exxyshop.com/products/ex-dt-01
Structure: square-section frame, slatted top running front-to-back,
closed end frames, low centre stretcher along the length.
"""
import bmesh

import lib

LENGTH = 1.80     # change to 2.10 for the long version
DEPTH = 0.90
HEIGHT = 0.75
PROFILE = 0.06    # square tube used for legs and apron
APRON = 0.065     # height of the top frame
SLAT_W = 0.030
SLAT_GAP = 0.024
SLAT_T = 0.02
RAIL = 0.05       # end frame foot rail
STRETCHER = 0.04


def build(color="#4b4f53"):
    mat = lib.powder_coat("EX-DT-01 powder coat", color)
    bm = bmesh.new()
    hx, hy, p = LENGTH / 2, DEPTH / 2, PROFILE

    # top frame (apron): two long sides, two short ends
    z_apron = HEIGHT - APRON / 2
    for sy in (-1, 1):
        lib.box(bm, (0, sy * (hy - p / 2), z_apron), (LENGTH, p, APRON))
    for sx in (-1, 1):
        lib.box(bm, (sx * (hx - p / 2), 0, z_apron), (p, DEPTH - 2 * p, APRON))

    # slats fill the opening, centred, flush with the top
    inner = LENGTH - 2 * p
    count = int((inner + SLAT_GAP) // (SLAT_W + SLAT_GAP))
    span = count * SLAT_W + (count - 1) * SLAT_GAP
    x0 = -span / 2 + SLAT_W / 2
    for i in range(count):
        lib.box(bm, (x0 + i * (SLAT_W + SLAT_GAP), 0, HEIGHT - SLAT_T / 2),
                (SLAT_W, DEPTH - 2 * p, SLAT_T))

    # legs: one at each corner, under the apron
    leg_h = HEIGHT - APRON
    for sx in (-1, 1):
        for sy in (-1, 1):
            lib.box(bm, (sx * (hx - p / 2), sy * (hy - p / 2), leg_h / 2), (p, p, leg_h))

    # end frames close at the floor with a foot rail
    for sx in (-1, 1):
        lib.box(bm, (sx * (hx - p / 2), 0, RAIL / 2), (p, DEPTH - 2 * p, RAIL))

    # centre stretcher sits on the foot rails
    lib.box(bm, (0, 0, RAIL + STRETCHER / 2), (LENGTH - 2 * p, STRETCHER, STRETCHER))

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    return lib.new_object("EX-DT-01", bm, mat, smooth_angle=30)
