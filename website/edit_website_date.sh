#!/bin/bash

cd /lfs/h2/emc/vpppg/save/alicia.bentley/gfs_realtime_maps/website

# 1. Copy the file to create a fresh version for updating
# This ensures website_original.php remains untouched
'cp' index_original.php index.php

YYYYMMDDHH=$1

echo "Processing Date: $YYYYMMDDHH"

# 5. Define the file and the target string
TARGET_FILE="index.php"
SEARCH_STR="2026012900"
REPLACE_STR="$YYYYMMDDHH"

# 4. Use sed to find and replace the string in-place
# The -i flag edits the file directly. 
if [ -f "$TARGET_FILE" ]; then
    sed -i "s/$SEARCH_STR/$REPLACE_STR/g" "$TARGET_FILE"
    echo "Update complete in $TARGET_FILE."
else
    echo "Error: $TARGET_FILE not found."
fi
