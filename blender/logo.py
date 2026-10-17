"""The EXXY mark, rebuilt as exact geometry from the original logo image.

Two X's woven together: a front X, and a second X shifted left that passes
under it. Where one band passes under another it is cut back by a thin gap.
Measurements are in pixels of the original 225 px image (mark is 58 px tall);
everything is drawn in painter's order, where "erase" cuts the gap.

One source for every use:
    python blender/logo.py web/public/exxy-logo.svg      # vector for the site
    python blender/logo.py renders/logo-check.png        # raster check (Pillow)
and terrace.py calls raster() for the wall texture.
"""
import sys

H = 58.0      # mark height
W = 7.0       # band width, measured horizontally
GAP = 2.2     # white gap where a band passes under another
TM_H = 7.6    # height of the trademark sign


def band(top_x, bottom_x, grow=0.0):
    """A diagonal band whose left edge runs from (top_x, 0) to (bottom_x, H)."""
    pad = 1.0 if grow else 0.0  # gap bands overshoot the ends so cuts are clean
    return [(top_x - grow, -pad), (top_x + W + grow, -pad),
            (bottom_x + W + grow, H + pad), (bottom_x - grow, H + pad)]


FRONT_DOWN = (15.0, 48.0)    # front X, "\"
FRONT_UP = (48.0, 15.0)      # front X, "/"
BACK_DOWN = (0.5, 33.5)      # back X, "\"
BACK_UP = (33.5, 0.5)        # back X, "/"


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def trademark():
    """Block letters T and M, top-aligned with the mark."""
    s = 1.45  # stroke
    t = [rect(59.0, 0, 64.4, s), rect(60.85, 0, 60.85 + s, TM_H)]
    m0, m1, mid = 65.6, 72.4, 69.0
    m = [rect(m0, 0, m0 + s, TM_H), rect(m1 - s, 0, m1, TM_H),
         [(m0, 0), (m0 + s, 0), (mid + s / 2, 5.4), (mid - s / 2, 5.4)],
         [(m1 - s, 0), (m1, 0), (mid + s / 2, 5.4), (mid - s / 2, 5.4)]]
    return t + m


# painter's order: the back "\" goes under the back "/", which goes under the front "\"
SHAPES = [
    ("add", band(*BACK_DOWN)),
    ("erase", band(*BACK_UP, grow=GAP)),
    ("add", band(*BACK_UP)),
    ("erase", band(*FRONT_DOWN, grow=GAP)),
    ("add", band(*FRONT_DOWN)),
    ("add", band(*FRONT_UP)),
] + [("add", p) for p in trademark()]

# bounds of the drawing (mark + trademark)
X0, X1, Y0, Y1 = 0.5, 72.4, 0.0, H
MARK_X1 = FRONT_UP[0] + W   # right edge of the mark alone, without the trademark


def svg(color="#000"):
    """Standalone SVG. Gaps are masks, so it stays one crisp shape at any size."""
    defs, body, n = [], "", 0
    view = f"{X0} {Y0} {X1 - X0} {Y1 - Y0}"
    for op, poly in SHAPES:
        pts = " ".join(f"{x:g},{y:g}" for x, y in poly)
        if op == "add":
            body += f'<polygon points="{pts}"/>'
        else:
            n += 1
            defs.append(
                f'<mask id="gap{n}" maskUnits="userSpaceOnUse" x="{X0 - 2}" y="{Y0 - 2}" '
                f'width="{X1 - X0 + 4}" height="{Y1 - Y0 + 4}">'
                f'<rect x="{X0 - 2}" y="{Y0 - 2}" width="{X1 - X0 + 4}" height="{Y1 - Y0 + 4}" fill="#fff"/>'
                f'<polygon points="{pts}" fill="#000"/></mask>')
            body = f'<g mask="url(#gap{n})">{body}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}" role="img" aria-label="EXXY">'
            f'<defs>{"".join(defs)}</defs><g fill="{color}">{body}</g></svg>\n')


def raster(height_px, supersample=3):
    """Coverage mask (0..1, top row first) of the whole drawing, `height_px` tall."""
    import numpy as np
    scale = height_px / (Y1 - Y0)
    w_px = int(round((X1 - X0) * scale))
    ss = supersample
    ys = (np.arange(height_px * ss) + 0.5) / (ss * scale) + Y0
    xs = (np.arange(w_px * ss) + 0.5) / (ss * scale) + X0
    out = np.zeros((height_px, w_px), np.float32)
    strip = 128 * ss  # in strips of whole output rows, to keep memory small
    for r0 in range(0, len(ys), strip):
        y = ys[r0:r0 + strip, None]
        x = xs[None, :]
        cover = np.zeros((len(y), len(xs)), bool)
        for op, poly in SHAPES:
            inside = np.ones_like(cover)
            for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
                inside &= (bx - ax) * (y - ay) - (by - ay) * (x - ax) >= 0
            cover = cover | inside if op == "add" else cover & ~inside
        rows = cover.reshape(len(y) // ss, ss, w_px, ss).mean(axis=(1, 3))
        out[r0 // ss:r0 // ss + len(rows)] = rows
    return out


if __name__ == "__main__":
    path = sys.argv[1]
    if path.endswith(".svg"):
        with open(path, "w", encoding="utf8") as f:
            f.write(svg())
    else:
        from PIL import Image
        a = raster(int(sys.argv[2]) if len(sys.argv) > 2 else 600)
        Image.fromarray(((1 - a) * 255).astype("uint8")).save(path)
    print("saved", path)
