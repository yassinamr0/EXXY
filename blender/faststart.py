"""Move an MP4's index (moov) in front of its media data, like ffmpeg's
-movflags +faststart. Blender's encoder writes the index at the end, so a
browser has to fetch the end of the file before it can show the first frame.

    python blender/faststart.py web/public/intro/portrait.mp4 [more.mp4 ...]

Rewrites each file in place; files that are already fast-start are left alone.
"""
import struct
import sys


def boxes(data, start, end):
    i = start
    while i < end:
        size, kind = struct.unpack(">I4s", data[i:i + 8])
        header = 8
        if size == 1:
            size, header = struct.unpack(">Q", data[i + 8:i + 16])[0], 16
        elif size == 0:
            size = end - i
        yield kind, i, size, header
        i += size


# boxes that only contain other boxes, on the way down to stco/co64
CONTAINERS = {b"moov", b"trak", b"mdia", b"minf", b"stbl"}


def shift_offsets(moov, start, end, delta):
    for kind, i, size, header in boxes(moov, start, end):
        if kind in CONTAINERS:
            shift_offsets(moov, i + header, i + size, delta)
        elif kind in (b"stco", b"co64"):
            body = i + header
            count = struct.unpack(">I", moov[body + 4:body + 8])[0]
            fmt, width = (">I", 4) if kind == b"stco" else (">Q", 8)
            for n in range(count):
                at = body + 8 + n * width
                value = struct.unpack(fmt, moov[at:at + width])[0] + delta
                if kind == b"stco" and value >= 2 ** 32:
                    raise ValueError("offset overflow: file needs co64")
                moov[at:at + width] = struct.pack(fmt, value)


def faststart(path):
    data = open(path, "rb").read()
    top = list(boxes(data, 0, len(data)))
    kinds = [k for k, *_ in top]
    if b"moov" not in kinds or b"mdat" not in kinds:
        raise ValueError(f"{path}: no moov/mdat")
    if kinds.index(b"moov") < kinds.index(b"mdat"):
        print("already fast-start:", path)
        return
    _, mi, msize, _ = top[kinds.index(b"moov")]
    moov = bytearray(data[mi:mi + msize])
    # everything from the first mdat on moves back by the size of moov
    shift_offsets(moov, 0, len(moov), msize)
    first_media = top[kinds.index(b"mdat")][1]
    rest = b"".join(data[i:i + s] for k, i, s, _ in top if k != b"moov" and i >= first_media)
    out = data[:first_media] + bytes(moov) + rest
    assert len(out) == len(data)
    open(path, "wb").write(out)
    print("fast-start:", path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        faststart(p)
