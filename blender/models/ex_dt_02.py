"""EX-DT-02 — oval teak-top dining table on two pedestals.

Listed: 180 x 85 x 75H cm or 240 x 90 x 75H cm; metal base, powder
electrostatic coated; teak top.
Reference photos: exxyshop.com/products/ex-dt-02
"""
import bmesh

import lib

LENGTH, WIDTH, HEIGHT = 2.40, 0.90, 0.75
TOP_T = 0.03


def build(color="#ece8e1"):
    base_mat = lib.powder_coat("EX-DT-02 base", color)
    bm = bmesh.new()
    for x in (-0.75, 0.75):
        lib.cylinder(bm, (x, 0, 0), 0.24, 0.018, 64)
        lib.cylinder(bm, (x, 0, 0.018), 0.035, HEIGHT - TOP_T - 0.018, 32)
    base = lib.new_object("EX-DT-02 base", bm, base_mat, smooth_angle=35)
    bm = bmesh.new()
    lib.slab(bm, lib.stadium(LENGTH, WIDTH, 24), HEIGHT - TOP_T, HEIGHT)
    top = lib.new_object("EX-DT-02 top", bm, lib.teak(), smooth_angle=35)
    bevel = top.modifiers.new("Bevel", "BEVEL")
    bevel.width = 0.008
    bevel.segments = 3
    return lib.assemble("EX-DT-02", [base, top])
