"""Join numbered PNG frames into an H.264 MP4 with Blender's built-in FFmpeg.

No separate ffmpeg install needed. Run inside the Blender app:
    blender --background --python blender/encode.py -- renders/glide/ renders/glide.mp4
"""
import argparse
import os
import sys

import bpy

FPS = 24


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frames", help="folder of numbered PNG frames")
    ap.add_argument("out", help="output .mp4")
    ap.add_argument("--quality", default="MEDIUM",
                    help="FFmpeg CRF preset: LOW, MEDIUM, HIGH, PERC_LOSSLESS")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    args = ap.parse_args(argv)

    folder = os.path.abspath(args.frames)
    names = sorted(f for f in os.listdir(folder) if f.lower().endswith(".png"))
    if not names:
        sys.exit(f"no PNG frames in {folder}")

    scene = bpy.context.scene
    edit = scene.sequence_editor_create()
    strip = edit.strips.new_image("frames", os.path.join(folder, names[0]), 1, 1)
    for name in names[1:]:
        strip.elements.append(name)
    w, h = strip.elements[0].orig_width, strip.elements[0].orig_height
    if not w:  # sizes are filled in lazily; read them from the image itself
        img = bpy.data.images.load(os.path.join(folder, names[0]))
        w, h = img.size

    scene.frame_start, scene.frame_end = 1, len(names)
    scene.render.fps = FPS
    scene.render.resolution_x, scene.render.resolution_y = w, h
    scene.render.resolution_percentage = 100
    scene.render.use_sequencer = True
    settings = scene.render.image_settings
    if hasattr(settings, "media_type"):  # Blender 5: pick video before the format
        settings.media_type = "VIDEO"
    settings.file_format = "FFMPEG"
    ff = scene.render.ffmpeg
    ff.format, ff.codec = "MPEG4", "H264"
    ff.constant_rate_factor = args.quality
    ff.audio_codec = "NONE"

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    scene.render.filepath = out
    bpy.ops.render.render(animation=True)
    print("saved", out)


if __name__ == "__main__":
    main()
