A Python tool that automatically organizes and renames images and videos by their date taken. It uses EXIF data for photos, ffprobe for videos, or falls back to filename parsing when necessary. Sorted files are placed into year-based subfolders (YYYY), and unrecognized/undateable files go to a “skipped” folder.

Features
Recursive Scanning of all subfolders under your source directory.
Automatic Renaming to YYYY-MM-DD HH.MM.SS.ext for consistent sorting.
Year-Based Folder Structure for quick chronological browsing.
Fallback Parsing of filenames like IMG_20230809_162453 or 20230809162453 if no metadata is found.
Skipped Folder for files that can’t be dated or have unsupported extensions.
