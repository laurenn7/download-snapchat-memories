# download-snapchat-memories
Download and restore your Snapchat Memories with correct dates, merged captions/stickers, and recovered GPS locations — plus a private local gallery viewer with a daily "years ago" flashback. 100% offline, no uploads, beginner-friendly.

Rescue Your Snapchat Memories

Snapchat's data export gives you your photos and videos back — but with broken captions, missing locations, and no good way to actually browse them. This guide walks you through fixing all of that, from a completely fresh start, using nothing but free tools and your own computer. No files ever leave your machine.

What you'll end up with:

All your Memories, downloaded with the correct dates
Captions and stickers merged permanently back onto their photos/videos
Real GPS locations restored to your files
A private, local "Memory Lane" viewer to scroll through everything — including a daily "X years ago" flashback

This guide is written for complete beginners. If you've never opened Terminal before, that's fine — every command is spelled out.

A note on why this exists: Snapchat's export format has changed over time, and most existing tutorials online are written for an older version. This guide reflects what Snapchat's export actually looks like as of 2026 — your files already come with correct timestamps, which simplifies things a lot compared to older guides.

What you'll need
A Mac (this guide is Mac-specific; the ideas transfer to Windows/Linux but the exact commands will differ)
About 15 minutes of active work, plus waiting time for Snapchat's export email (can take minutes to over a day)
No coding experience required
Step 1: Open Terminal

Terminal is a normal Mac app for typing commands — it's not dangerous. Press Cmd + Space, type Terminal, press Enter. A window with a blinking cursor opens. You'll type each command below and press Enter to run it.

Step 2: Install the tools you'll need

Check what you already have by typing these one at a time:

git --version
python3 --version

If either says "command not found," install Homebrew (a package manager for Mac) by pasting this into Terminal and pressing Enter:

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/brew/HEAD/install.sh)"

It'll ask for your Mac password (typing shows nothing on screen — that's normal). Once it finishes, install the tools:

brew install python git exiftool ffmpeg

If it asks Do you want to proceed? [y/n], type y and press Enter — it's just listing what it's about to install.

Step 3: Download this project
cd ~/Desktop
git clone https://github.com/laurenn7/download-snapchat-memories.git
cd download-snapchat-memories

Set up a clean workspace for it:

python3 -m venv .venv
source .venv/bin/activate
pip install pillow

You'll know it worked when your prompt starts with (.venv). You'll need to run that source .venv/bin/activate line again anytime you close and reopen Terminal to keep working on this.

Step 4: Request your data from Snapchat

In your browser, go to accounts.snapchat.com and log in.

Click My Data
Click Export your Memories, then choose Request Only Memories
Set the date range to All Time
Confirm your email and click Submit

Now you wait — Snapchat emails you a download link once it's ready (minutes to over a day, depending on how much you've saved).

Step 5: Unzip and find your files

When the email arrives, download and unzip the file(s) it gives you (macOS unzips automatically when you double-click). Inside, look for:

A folder called memories — your actual photos and videos
A file called memories_history_all_locations.html — a table of every memory's date and GPS location (no download links; the media is already included in the memories folder directly)

Both should be right inside the main unzipped folder. Keep the memories folder as-is for now — don't move or rename anything inside it.

Step 6: Merge captions and stickers back onto your photos/videos

Snapchat exports captions and text overlays as separate transparent PNG files, rather than baking them into the photo or video. merge_overlays.py (included in this repo) finds matching pairs and combines them permanently.

In Terminal, with (.venv) still showing in your prompt:

python3 merge_overlays.py

Type that with a trailing space, then drag your memories folder from Finder into the Terminal window (this fills in the full path automatically), then press Enter.

You'll see a line print for each file it merges. When it finishes, it prints a summary and creates a new folder ending in _combined — that's your complete, merged set.

Step 7: Restore GPS locations

add_gps.py matches each file to its row in the locations HTML file by exact capture timestamp (this works because your files already carry the correct date and time), and writes the coordinates directly into the file.

python3 add_gps.py

Trailing space, then drag in your memories_history_all_locations.html file, then drag in the _combined folder from Step 6, then press Enter.

When it finishes, it prints how many files were successfully matched and tagged.

Step 8: Browse everything in Memory Lane

Open memory_lane.html (in this repo) by double-clicking it — it opens in your default browser. Click "Choose your memories folder" and select your _combined folder from Step 6.

You'll get a scrollable, month-by-month gallery with a year index on the side. Click anything to view it full-screen with its date and location. If today's date matches something from a past year, you'll see a flashback banner at the top — your own "X years ago" moment.

Important: always open this file directly (double-click it, or drag it into a browser tab) rather than viewing it inside another app's preview panel — it needs real access to your files and, for locations, to the internet.

Troubleshooting

Homebrew or the installer asks [y/n] — that's normal, just type y and press Enter.

Not sure where a downloaded file is — browser downloads land in your Downloads folder by default. You can also type cd  (with a trailing space) in Terminal, then drag any file or folder from Finder into the window to auto-fill its full path.

merge_overlays.py doesn't merge anything — open one of your PNG overlay filenames and check whether it ends in -overlay.png, with a matching photo/video ending in -main.ext sharing the same ID. If the naming looks different, that's worth an issue on this repo.

A video's location looks wrong — Snapchat's location data is only as accurate as what your phone recorded at the time; this can't fix occasionally imprecise GPS.

Your export already has correct dates — good, that's expected as of 2026. If a much older guide told you to expect a memories_history.html with individual download links instead, Snapchat has since changed its export format — this guide reflects the current one.

What's in this repo
File	What it does
merge_overlays.py	Merges caption/sticker PNGs onto their base photo or video
add_gps.py	Matches files to the locations HTML by timestamp and writes GPS data into each file
memory_lane.html	A private, local gallery viewer with month/year browsing and a daily flashback

All three run entirely on your own computer. Nothing is uploaded anywhere.

Privacy

This entire process is local. merge_overlays.py and add_gps.py only touch files on your computer. memory_lane.html reads your files directly in your browser and never uploads them — the only network request it makes is a location name lookup (coordinates only, not your photos) sent to OpenStreetMap's Nominatim service when you open a memory that has GPS data.
