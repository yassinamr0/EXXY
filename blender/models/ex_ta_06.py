"""EX-TA-06 — round bistro table on a sculpted pedestal.

Listed: diameter 80 cm, height 75 cm (drawing: base 45 x 45), metal,
powder electrostatic coated.
Reference photos: exxyshop.com/products/ex-ta-06
"""
import bmesh

import lib

HEIGHT = 0.75


def build(color="#2f3134"):
    mat = lib.powder_coat("EX-TA-06 powder coat", color)
    bm = bmesh.new()
    lib.slab(bm, lib.ellipse(0.40, 0.40, 64), HEIGHT - 0.014, HEIGHT)
    lib.cylinder(bm, (0, 0, 0), 0.225, 0.012, 64)        # base plate
    lib.cylinder(bm, (0, 0, 0.012), 0.075, 0.17, 40)     # lower bulb body
    sphere = bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=0.075)
    bmesh.ops.translate(bm, vec=(0, 0, 0.182), verts=sphere["verts"])  # domed top of the bulb
    lib.cylinder(bm, (0, 0, 0.2), 0.03, HEIGHT - 0.214, 32)
    return lib.new_object("EX-TA-06", bm, mat, smooth_angle=35)
