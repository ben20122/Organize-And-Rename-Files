"""
Organize Media Script
=====================

A Python script to recursively scan a folder (and its subfolders),
look for images and videos, determine the date they were taken
(either from EXIF data for images or 'creation_time' via ffprobe for videos),
and then rename them to "YYYY-MM-DD HH.MM.SS.ext" and place them
into a year-based folder structure.

DEPENDENCIES
------------
- Python 3.7+
- Pillow (for EXIF reading) => pip install pillow
- ffmpeg (which provides ffprobe) => must be installed and on PATH

CONFIGURATION
-------------
Edit the three variables in the CONFIG section:

1. SOURCE_FOLDER:      Where to search for your files (recursively).
2. ORGANIZED_FOLDER:   Where organized files should be placed.
3. SKIPPED_FOLDER:     Where files go if they're missing valid metadata or unsupported.

Example usage:
    organize_and_rename_files.py
"""

import os
import shutil
import datetime
import re
import subprocess
import json

# For reading image EXIF data (install with `pip install pillow`).
from PIL import Image
from PIL.ExifTags import TAGS

##############################################################################
# CONFIG: CUSTOMIZE THESE PATHS
##############################################################################
SOURCE_FOLDER = r"PATH_TO_YOUR_MEDIA_FOLDER"
ORGANIZED_FOLDER = r"PATH_WHERE_ORGANIZED_FILES_GO"
SKIPPED_FOLDER = r"PATH_WHERE_SKIPPED_FILES_GO"


##############################################################################
# 1) HELPER FUNCTIONS
##############################################################################

def create_skipped_folder():
    """
    Ensures SKIPPED_FOLDER exists and returns its path.
    """
    if not os.path.exists(SKIPPED_FOLDER):
        os.makedirs(SKIPPED_FOLDER)
    return SKIPPED_FOLDER

def move_to_skipped(file_path, reason="No valid date found"):
    """
    Moves the file (retaining its original name) into SKIPPED_FOLDER.
    """
    skipped_folder = create_skipped_folder()
    destination = os.path.join(skipped_folder, os.path.basename(file_path))
    print(f"Skipping file ({reason}): {os.path.basename(file_path)}")
    shutil.move(file_path, destination)

def generate_new_file_name(date_obj, file_ext):
    """
    Given a valid datetime and an extension, returns a string:
    'YYYY-MM-DD HH.MM.SS.ext'
    """
    return date_obj.strftime("%Y-%m-%d %H.%M.%S") + file_ext


##############################################################################
# 2) DATE/TIME EXTRACTION (FILENAME PARSING, IMAGE EXIF, VIDEO METADATA)
##############################################################################

def parse_date_from_filename(filename):
    """
    If no metadata is found, try these filename patterns:
      1) (\\d{8})_(\\d{6})  => e.g. 'IMG_0033_20230809_162453'
      2) (\\d{14})         => e.g. '20230809162453'
    Returns a datetime if matched, else None.
    """
    # Pattern A: 'YYYYMMDD_HHMMSS' => 8 digits, underscore, 6 digits
    match_a = re.search(r"(\d{8})_(\d{6})", filename)
    if match_a:
        part1, part2 = match_a.groups()
        try:
            year = int(part1[:4])
            month = int(part1[4:6])
            day = int(part1[6:8])
            hour = int(part2[:2])
            minute = int(part2[2:4])
            second = int(part2[4:6])
            return datetime.datetime(year, month, day, hour, minute, second)
        except ValueError:
            pass

    # Pattern B: 'YYYYMMDDHHMMSS' => 14 digits in a row
    match_b = re.search(r"(\d{14})", filename)
    if match_b:
        digits = match_b.group(1)
        try:
            year = int(digits[0:4])
            month = int(digits[4:6])
            day = int(digits[6:8])
            hour = int(digits[8:10])
            minute = int(digits[10:12])
            second = int(digits[12:14])
            return datetime.datetime(year, month, day, hour, minute, second)
        except ValueError:
            pass

    return None

def get_image_exif_date(image_path):
    """
    Reads 'DateTimeOriginal' EXIF tag from an image using Pillow.
    If missing, returns None.
    """
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'DateTimeOriginal':
                        # Typically 'YYYY:MM:DD HH:MM:SS'
                        return datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
        return None
    except Exception as e:
        print(f"Error reading EXIF from {os.path.basename(image_path)}: {e}")
        return None

def get_video_ffprobe_date(video_path):
    """
    Uses ffprobe to read the 'creation_time' from video container metadata.
    If missing or error, returns None.

    Make sure ffprobe is installed and on PATH (ffmpeg suite).
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_entries", "format_tags=creation_time",
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return None

        info = json.loads(result.stdout)
        tags = info.get("format", {}).get("tags", {})
        creation_str = tags.get("creation_time")
        if not creation_str:
            return None

        # e.g. "2023-08-09T16:24:53.000000Z" -> "2023-08-09 16:24:53"
        creation_str = creation_str.replace('Z', '')
        creation_str = creation_str.replace('T', ' ')
        creation_str = creation_str[:19]

        return datetime.datetime.strptime(creation_str, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error using ffprobe on {os.path.basename(video_path)}: {e}")
        return None


##############################################################################
# 3) ORGANIZE LOGIC (IMAGES / VIDEOS)
##############################################################################

def organize_images(file_path):
    """
    1) Get EXIF date from image
    2) If no EXIF, parse date from filename
    3) If still no date, skip
    4) Otherwise rename to 'YYYY-MM-DD HH.MM.SS.ext' and move to ORGANIZED_FOLDER\YYYY
    """
    date_taken = get_image_exif_date(file_path)
    if not date_taken:
        # fallback: parse from filename
        filename_only = os.path.splitext(os.path.basename(file_path))[0]
        date_taken = parse_date_from_filename(filename_only)

    if not date_taken:
        move_to_skipped(file_path, "No date from EXIF or filename")
        return

    year_folder = date_taken.strftime("%Y")
    target_folder = os.path.join(ORGANIZED_FOLDER, year_folder)
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    file_ext = os.path.splitext(file_path)[1]
    new_file_name = generate_new_file_name(date_taken, file_ext)

    print(f"Organizing image: {os.path.basename(file_path)} -> {new_file_name}")
    shutil.move(file_path, os.path.join(target_folder, new_file_name))

def organize_videos(file_path):
    """
    1) Get 'creation_time' via ffprobe
    2) If missing, parse date from filename
    3) If still no date, skip
    4) Otherwise rename and move to ORGANIZED_FOLDER\YYYY
    """
    date_taken = get_video_ffprobe_date(file_path)
    if not date_taken:
        filename_only = os.path.splitext(os.path.basename(file_path))[0]
        date_taken = parse_date_from_filename(filename_only)

    if not date_taken:
        move_to_skipped(file_path, "No date from ffprobe or filename")
        return

    year_folder = date_taken.strftime("%Y")
    target_folder = os.path.join(ORGANIZED_FOLDER, year_folder)
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    file_ext = os.path.splitext(file_path)[1]
    new_file_name = generate_new_file_name(date_taken, file_ext)

    print(f"Organizing video: {os.path.basename(file_path)} -> {new_file_name}")
    shutil.move(file_path, os.path.join(target_folder, new_file_name))


##############################################################################
# 4) MAIN LOGIC (RECURSIVE SCAN)
##############################################################################

def process_file(file_path):
    """
    Check if it's an image or video, then call the organizer.
    Otherwise, skip.
    """
    lower = file_path.lower()
    print(f"Processing file: {file_path}")

    if lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.heic')):
        organize_images(file_path)
    elif lower.endswith(('.mp4', '.mov', '.avi', '.mkv')):
        organize_videos(file_path)
    else:
        move_to_skipped(file_path, "Unsupported file type")

def main():
    print(f"Starting recursive scan in '{SOURCE_FOLDER}'")

    for root, dirs, files in os.walk(SOURCE_FOLDER):
        print(f"\nNow scanning folder: {root}")
        print(f"  Contains {len(files)} file(s) and {len(dirs)} subfolder(s).")

        for file_name in files:
            file_path = os.path.join(root, file_name)
            if os.path.isfile(file_path):
                try:
                    process_file(file_path)
                except Exception as e:
                    print(f"Error processing '{file_path}': {e}")

    print("\nDone processing all subfolders!")

if __name__ == "__main__":
    main()
