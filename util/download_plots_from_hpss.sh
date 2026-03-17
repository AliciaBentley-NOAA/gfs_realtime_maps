#!/bin/bash

# --- Configuration ---
START_DATE="2026022406"  # YYYYMMDDHH
END_DATE="2026030500"    # YYYYMMDDHH

INCREMENT_SEC=$(( 6 * 3600 )) # 21600 seconds

# Get the raw start and end timestamps in UTC
start_unix=$(date -u -d "${START_DATE:0:8} ${START_DATE:8:2}" +%s)
end_unix=$(date -u -d "${END_DATE:0:8} ${END_DATE:8:2}" +%s)

# --- The Loop ---
# seq will generate every timestamp from start to end in 6-hour steps
for current_unix in $(seq $start_unix $INCREMENT_SEC $end_unix); do

    # Turn the timestamp into the YYYYMMDDHH format
    DATE_STR=$(date -u -d "@$current_unix" +%Y%m%d%H)

    echo "Processing: $DATE_STR"

    # Download and untar plots from HPSS onto WCOSS2
    echo "htar -xvf /NCEPDEV/ovp/2year/alicia.bentley/gfsv17_realtime_plots/${DATE_STR}.tar"
    htar -xvf /NCEPDEV/ovp/2year/alicia.bentley/gfsv17_realtime_plots/${DATE_STR}.tar

done

echo "Done!"
