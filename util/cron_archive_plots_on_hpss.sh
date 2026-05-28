#!/bin/bash

# --- Configuration ---
cd /lfs/h2/emc/vpppg/noscrub/alicia.bentley/gfs_realtime_maps/maps/gfs

date --date="1 day ago" +%Y%m%d > holddate.txt
ymd=`cut -c 1-8 holddate.txt` # YYYYMMDD
echo $ymd

INCREMENT_SEC=$(( 6 * 3600 )) # 21600 seconds

# Get the raw start and end timestamps in UTC
start_unix=$(date -u -d "${ymd:0:8} 00" +%s)
end_unix=$(date -u -d "${ymd:0:8} 18" +%s)

# --- The Loop ---
# seq will generate every timestamp from start to end in 6-hour steps
for current_unix in $(seq $start_unix $INCREMENT_SEC $end_unix); do

    # Turn the timestamp into the YYYYMMDDHH format
    DATE_STR=$(date -u -d "@$current_unix" +%Y%m%d%H)

    echo "Processing: $DATE_STR"

    if [ -d "$DATE_STR" ]; then
        # Copy plots from WCOSS2 to HPSS
        echo "htar -cvf /NCEPDEV/ovp/2year/alicia.bentley/gfsv17_realtime_plots/${DATE_STR}.tar ${DATE_STR}/"
        htar -cvf /NCEPDEV/ovp/2year/alicia.bentley/gfsv17_realtime_plots/${DATE_STR}.tar ${DATE_STR}/
    else
        echo "   --> Skipping: Directory $DATE_STR not found."
    fi

done

echo "Done!"
