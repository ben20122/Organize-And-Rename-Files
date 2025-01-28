Organize Media Script
A Python tool that automatically organizes and renames images and videos by their date taken. It uses EXIF data for photos, ffprobe for videos, or falls back to filename parsing when necessary. Sorted files are placed into year-based subfolders (YYYY), and unrecognized/undateable files go to a “skipped” folder.

Features
Recursive Scanning of all subfolders under your source directory.
Automatic Renaming to YYYY-MM-DD HH.MM.SS.ext for consistent sorting.
Year-Based Folder Structure for quick chronological browsing.
Fallback Parsing of filenames like IMG_20230809_162453 or 20230809162453 if no metadata is found.
Skipped Folder for files that can’t be dated or have unsupported extensions.
Requirements
Python 3.7+
Pillow (for image EXIF)
bash
Copy
Edit
pip install pillow
FFmpeg (including ffprobe), installed and on your PATH.
Test with:
bash
Copy
Edit
ffprobe -version
Configuration
Open organize_media.py and set the top three variables:

python
Copy
Edit
SOURCE_FOLDER = r"PATH_TO_YOUR_MEDIA_FOLDER"
ORGANIZED_FOLDER = r"PATH_WHERE_ORGANIZED_FILES_GO"
SKIPPED_FOLDER = r"PATH_WHERE_SKIPPED_FILES_GO"
SOURCE_FOLDER: Folder containing your images/videos.
ORGANIZED_FOLDER: Where the script will create subfolders named after each file’s year.
SKIPPED_FOLDER: Folder for files that the script can’t determine a valid date for.
Usage
Clone or Download this repository.
Install Dependencies:
bash
Copy
Edit
pip install pillow
(Ensure ffprobe is installed and in PATH.)
Run the script:
bash
Copy
Edit
python organize_media.py
The script will:
Recursively traverse SOURCE_FOLDER.
Identify each file’s date using EXIF/ffprobe/filename.
Rename it to YYYY-MM-DD HH.MM.SS.ext.
Move it into ORGANIZED_FOLDER/<year>.
Skip unrecognized or missing-date files to SKIPPED_FOLDER.
Troubleshooting
No metadata or date parsed? The file goes to “skipped” so you can handle it manually.
Slow or stuck on a large video? ffprobe is usually quick, but if you encounter issues, verify the video’s integrity or try a different tool.
No output? Double-check you have files with recognized extensions (.jpg, .mp4, etc.) in your source folder.
