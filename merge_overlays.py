#!/usr/bin/env python3
"""
Merges Snapchat memory overlays (captions/stickers/text, exported as separate
PNG files) onto their matching base photo or video.

Usage:
    python3 merge_overlays.py /path/to/memories

Output goes to a new "combined" folder next to your memories folder.
Files with no matching overlay are copied through unchanged, so the output
folder ends up as one complete, ready-to-use set.
"""

import sys
import os
import re
import shutil
import subprocess
from pathlib import Path

IMG_EXT = {'.jpg', '.jpeg', '.png', '.heic', '.heif'}
VID_EXT = {'.mp4', '.mov', '.m4v'}


def find_key(filename: str):
    """Strip -main / -overlay suffix to get the shared id for a pair."""
    stem = Path(filename).stem
    m = re.match(r'^(.*)-(main|overlay)$', stem, re.IGNORECASE)
    if m:
        return m.group(1), m.group(2).lower()
    return stem, None


def merge_image(main_path: Path, overlay_path: Path, out_path: Path):
    from PIL import Image
    base = Image.open(main_path).convert('RGBA')
    overlay = Image.open(overlay_path).convert('RGBA')
    if overlay.size != base.size:
        overlay = overlay.resize(base.size)
    combined = Image.alpha_composite(base, overlay).convert('RGB')
    combined.save(out_path, quality=95)


def merge_video(main_path: Path, overlay_path: Path, out_path: Path):
    # scale2ref resizes the overlay to match the video's actual resolution
    # before compositing -- without this, overlays exported at a different
    # size than the video get cropped instead of fitted.
    cmd = [
        'ffmpeg', '-y', '-loglevel', 'error',
        '-i', str(main_path),
        '-i', str(overlay_path),
        '-filter_complex', '[1:v][0:v]scale2ref[ov][base];[base][ov]overlay=0:0:format=auto',
        '-codec:a', 'copy',
        str(out_path)
    ]
    subprocess.run(cmd, check=True)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 merge_overlays.py /path/to/memories")
        sys.exit(1)

    src_dir = Path(sys.argv[1]).expanduser().resolve()
    if not src_dir.is_dir():
        print(f"Not a folder: {src_dir}")
        sys.exit(1)

    out_dir = src_dir.parent / (src_dir.name + "_combined")
    out_dir.mkdir(exist_ok=True)

    # group files by shared key
    groups = {}
    for f in src_dir.iterdir():
        if not f.is_file():
            continue
        key, role = find_key(f.name)
        groups.setdefault(key, {})[role or 'plain'] = f

    merged_count = 0
    copied_count = 0
    failed = []

    for key, roles in groups.items():
        main_f = roles.get('main') or roles.get('plain')
        overlay_f = roles.get('overlay')

        if main_f is None:
            continue

        ext = main_f.suffix.lower()

        if overlay_f is not None and ext in IMG_EXT.union(VID_EXT):
            out_path = out_dir / main_f.name.replace('-main', '')
            try:
                if ext in IMG_EXT:
                    merge_image(main_f, overlay_f, out_path)
                else:
                    merge_video(main_f, overlay_f, out_path)
                # preserve the original timestamp so it still sorts correctly
                stat = os.stat(main_f)
                os.utime(out_path, (stat.st_atime, stat.st_mtime))
                merged_count += 1
                print(f"Merged: {out_path.name}")
            except Exception as e:
                failed.append((main_f.name, str(e)))
        else:
            # no overlay to merge — just copy through
            out_path = out_dir / main_f.name
            if not out_path.exists():
                shutil.copy2(main_f, out_path)
                copied_count += 1

    print(f"\nDone. Merged {merged_count} pairs, copied {copied_count} single files.")
    if failed:
        print(f"\n{len(failed)} failed:")
        for name, err in failed:
            print(f"  {name}: {err}")
    print(f"\nOutput folder: {out_dir}")


if __name__ == '__main__':
    main()
