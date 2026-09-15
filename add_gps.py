#!/usr/bin/env python3
"""
Matches each photo/video in a folder to its row in Snapchat's
memories_history.html (locations export) by exact capture timestamp,
then writes the GPS coordinates into the file's metadata using exiftool.

Matching works because each file's own modification date (already
confirmed accurate) is the exact same moment as the "Date" column in
the HTML, down to the second.

Usage:
    python3 add_gps.py /path/to/memories_history_all_locations.html /path/to/memories_combined
"""

import sys
import os
import re
import subprocess
import datetime
from pathlib import Path

IMG_EXT = {'.jpg', '.jpeg', '.png', '.heic', '.heif'}
VID_EXT = {'.mp4', '.mov', '.m4v'}

ROW_RE = re.compile(
    r'<tr><td>([\d-]+ [\d:]+) UTC</td><td>(Image|Video)</td>'
    r'<td>Latitude, Longitude: ([-\d.]+), ([-\d.]+)</td>'
)


def parse_html(html_path: Path):
    with open(html_path, encoding='utf-8') as f:
        content = f.read()
    lookup = {}
    for date_str, _media_type, lat, lon in ROW_RE.findall(content):
        lat, lon = float(lat), float(lon)
        if lat == 0.0 and lon == 0.0:
            continue
        lookup.setdefault(date_str, []).append((lat, lon))
    return lookup


def write_gps(file_path: Path, lat: float, lon: float):
    ext = file_path.suffix.lower()
    if ext in VID_EXT:
        # QuickTime (mp4/mov) has no separate Ref tag -- the signed value
        # alone is correct here, and adding an explicit Ref tag breaks it.
        cmd = [
            'exiftool', '-overwrite_original', '-P',
            f'-GPSLatitude={lat}',
            f'-GPSLongitude={lon}',
            str(file_path)
        ]
    else:
        # EXIF (jpg/png/heic) needs the magnitude and an explicit Ref tag --
        # writing a signed value alone here can leave the Ref tag unset,
        # which defaults readers to North/East regardless of the true sign.
        lat_ref = 'N' if lat >= 0 else 'S'
        lon_ref = 'E' if lon >= 0 else 'W'
        cmd = [
            'exiftool', '-overwrite_original', '-P',
            f'-GPSLatitude={abs(lat)}', f'-GPSLatitudeRef={lat_ref}',
            f'-GPSLongitude={abs(lon)}', f'-GPSLongitudeRef={lon_ref}',
            str(file_path)
        ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 add_gps.py /path/to/memories_history_all_locations.html /path/to/memories_folder")
        sys.exit(1)

    html_path = Path(sys.argv[1]).expanduser().resolve()
    folder = Path(sys.argv[2]).expanduser().resolve()

    if not html_path.is_file():
        print(f"HTML file not found: {html_path}")
        sys.exit(1)
    if not folder.is_dir():
        print(f"Folder not found: {folder}")
        sys.exit(1)

    print("Parsing location data...")
    lookup = parse_html(html_path)
    print(f"Loaded {sum(len(v) for v in lookup.values())} located memories from the HTML file.\n")

    matched = 0
    no_location_in_table = 0
    no_match = 0
    failed = []

    for f in sorted(folder.iterdir()):
        if not f.is_file():
            continue
        ext = f.suffix.lower()
        if ext not in IMG_EXT.union(VID_EXT):
            continue
        if 'overlay' in f.name.lower():
            continue

        mtime = f.stat().st_mtime
        utc_dt = datetime.datetime.utcfromtimestamp(mtime)
        key = utc_dt.strftime('%Y-%m-%d %H:%M:%S')

        candidates = lookup.get(key)
        if not candidates:
            no_match += 1
            continue

        lat, lon = candidates[0]
        ok = write_gps(f, lat, lon)
        if ok:
            matched += 1
            print(f"Located: {f.name}  ->  {lat}, {lon}")
        else:
            failed.append(f.name)

    print(f"\nDone.")
    print(f"  Matched and tagged: {matched}")
    print(f"  No matching timestamp in HTML: {no_match}")
    if failed:
        print(f"  Failed to write ({len(failed)}):")
        for name in failed:
            print(f"    {name}")


if __name__ == '__main__':
    main()
