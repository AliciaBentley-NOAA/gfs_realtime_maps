#!/bin/bash

# 1. Copy the file to create a fresh version for updating
# This ensures website_original.php remains untouched
'cp' index_original.php index.php

# 2. Read the date string from the parent directory
DATE_FILE="../holddate.txt"

if [ -f "$DATE_FILE" ]; then
    DATE_STR=$(cat "$DATE_FILE" | tr -d '\r ')
else
    echo "Error: Cannot find $DATE_FILE in ../ directory"
    exit 1
fi

# 3. Slice the string using parameter expansion ${var:offset:length}
YYYY=${DATE_STR:0:4}
MM=${DATE_STR:4:2}
DD=${DATE_STR:6:2}

# 4. Capture the first command-line argument as CYC
# If no argument is provided, this will be empty
CYC=$1

echo "Processing Date: Year=$YYYY, Month=$MM, Day=$DD, Cycle=$CYC"

# 5. Define the file and the target string
TARGET_FILE="index.php"
SEARCH_STR="2026012900"
REPLACE_STR="$YYYY$MM$DD$CYC"

# 4. Use sed to find and replace the string in-place
# The -i flag edits the file directly. 
if [ -f "$TARGET_FILE" ]; then
    sed -i "s/$SEARCH_STR/$REPLACE_STR/g" "$TARGET_FILE"
    echo "Update complete in $TARGET_FILE."
else
    echo "Error: $TARGET_FILE not found."
fi
