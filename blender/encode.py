"""Join numbered PNG frames into a web video with Blender's built-in FFmpeg.

No separate ffmpeg install needed. Run inside the Blender app:
    blender --background --python blender/encode.py -- renders/glide/ out/portrait.mp4
    blender --background --python blender/encode.py -- renders/glide/ out/portrait.webm
    blender --background --python blender/encode.py -- renders/glide/ out/portrait.mp4 --stills out/portrait

The container follows the extension: .mp4 is H.264 (plays everywhere), .webm is
VP9 (smaller, for Chrome/Firefox/Android). --stills also writes PREFIX-start.jpg
(poster shown while the video loads) and PREFIX-end.jpg (the landed view, for
reduced motion and after the video ends).
"""
import argparse
import os
import sys

import bpy

FPS = 24
CODECS = {".mp4": ("MPEG4", "H264"), ".webm": ("WEBM", "WEBM")}


def save_jpeg(scene, src, dst, quality=82):
    settings = scene.render.image_settings
    if hasattr(settings, "media_type"):
        settings.media_type = "IMAGE"
    settings.file_format, settings.quality = "JPEG", quality
    settings.color_mode = "RGB"
    img = bpy.data.images.load(src)
    img.save_render(dst, scene=scene)
    print("saved", dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frames", help="folder of numbered PNG frames")
    ap.add_argument("out", help="output .mp4 or .webm")
    ap.add_argument("--quality", default="MEDIUM",
                    help="FFmpeg CRF preset: LOW, MEDIUM, HIGH, PERC_LOSSLESS")
    ap.add_argument("--stills", metavar="PREFIX", help="also save PREFIX-start.jpg / PREFIX-end.jpg")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    args = ap.parse_args(argv)

    folder = os.path.abspath(args.frames)
    names = sorted(f for f in os.listdir(folder) if f.lower().endswith(".png"))
    if not names:
        sys.exit(f"no PNG frames in {folder}")
    ext = os.path.splitext(args.out)[1].lower()
    if ext not in CODECS:
        sys.exit(f"unsupported output {ext}: use .mp4 or .webm")

    scene = bpy.context.scene
    # the frames are already finished pictures: pass them through untouched
    # (the default AgX view would tone-map them a second time and turn white grey)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
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
    ff.format, ff.codec = CODECS[ext]
    ff.constant_rate_factor = args.quality
    ff.audio_codec = "NONE"

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    scene.render.filepath = out
    bpy.ops.render.render(animation=True)
    print("saved", out)

    if args.stills:
        prefix = os.path.abspath(args.stills)
        save_jpeg(scene, os.path.join(folder, names[0]), prefix + "-start.jpg")
        save_jpeg(scene, os.path.join(folder, names[-1]), prefix + "-end.jpg")


if __name__ == "__main__":
    main()
