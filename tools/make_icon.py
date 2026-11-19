#!/usr/bin/env python3
"""Build the Bumper window icon from assets/eye-source.png."""

from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


def tight_square(img, threshold=25, fill=0.95):
    grey = img.convert("L").point(lambda p: 255 if p > threshold else 0)
    box = grey.getbbox()
    if not box:
        return img

    left, top, right, bottom = box
    side = int(max(right - left, bottom - top) / fill)
    cx = (left + right) // 2
    cy = (top + bottom) // 2
    x0 = max(0, cx - side // 2)
    y0 = max(0, cy - side // 2)
    return img.crop((x0, y0, x0 + side, y0 + side))


def main():
    source = Image.open(ASSETS / "eye-source.png").convert("RGB")
    master = tight_square(source)
    master = master.resize((512, 512), Image.LANCZOS)

    master.save(ASSETS / "icon.png")
    master.save(
        ASSETS / "icon.ico",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )
    master.save(ROOT / "web" / "icon.png")
    print("bumper icons written")


if __name__ == "__main__":
    main()
