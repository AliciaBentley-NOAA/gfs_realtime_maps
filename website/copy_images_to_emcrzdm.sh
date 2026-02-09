#!/bin/bash

# 1. Determine current UTC hour
current_hour=$(date -u +%H)
current_date=$(date -u +%Y%m%d)

# 2. Logic to determine start_hh and start_date
if [ "$current_hour" -ge 5 ] && [ "$current_hour" -lt 11 ]; then
    start_hh="00"
    start_date=$(date -u -d "today" +%Y%m%d)
elif [ "$current_hour" -ge 11 ] && [ "$current_hour" -lt 17 ]; then
    start_hh="06"
    start_date=$(date -u -d "today" +%Y%m%d)
elif [ "$current_hour" -ge 17 ] && [ "$current_hour" -lt 23 ]; then
    start_hh="12"
    start_date=$(date -u -d "today" +%Y%m%d)
else
    # Covers 23Z, 00Z, 01Z, 02Z, 03Z, 04Z
    start_hh="18"
    if [ "$current_hour" -lt 5 ]; then
        start_date=$(date -u -d "yesterday" +%Y%m%d)
    else
        start_date=$(date -u -d "today" +%Y%m%d)
    fi
fi

start_date="20260209"
start_hh="06"

echo "Most recent run: ${start_date}${start_hh}"

# 3. Define and Echo Plot Types
#plot_types=("mslp" "500Z" "850T")
plot_type=$1
echo "------------------------------------------------"
#echo "Copying Plot Types: ${plot_types[@]}"
echo "Copying Plot Types: ${plot_type}"
echo "------------------------------------------------"

# 4. Convert Anchor to Epoch Seconds
# This is our "Zero Point"
anchor_seconds=$(date -u -d "${start_date} ${start_hh}:00:00" +%s)

echo "------------------------------------------------"
echo "Anchor Run: ${start_date} ${start_hh}Z"
echo "------------------------------------------------"

# 5. Loop 192 hours BACKWARD in 6-hour steps
for (( h=0; h<=192; h+=6 )); do
    
# Calculate target time in seconds
    seconds_to_subtract=$(( h * 3600 ))
    target_seconds=$(( anchor_seconds - seconds_to_subtract ))

    # Convert back to YYYYMMDD and HH
    YYYYMMDD=$(date -u -d "@${target_seconds}" +%Y%m%d)
    HH=$(date -u -d "@${target_seconds}" +%H)
    
    # Format FFF (the offset from anchor)
    # This increments by 006 every loop regardless of directory presence
    FFF=$(printf "%03d" $h)

#    for plot_type in "${plot_types[@]}"; do
        local_path="/lfs/h2/emc/vpppg/noscrub/alicia.bentley/gfs_realtime_maps/maps/gfs/${YYYYMMDD}${HH}/conus/${plot_type}"
        remote_path="/home/people/emc/www/htdocs/users/meg/gfsv17/realtime/images/conus/${plot_type}/p${FFF}"
        
        if [ -d "$local_path" ]; then
            echo "Copying to emcrzdm: ${YYYYMMDD}${HH} | Offset: p${FFF} | conus | Type: ${plot_type}"
            
            # 1. Remotely remove old images in that specific FFF folder
            ssh abentley@emcrzdm "rm -f ${remote_path}/image*.png"
            
            # 2. Perform the transfer
            scp -r ${local_path}/image*.png abentley@emcrzdm:${remote_path}/.
        else
            echo "Skipping Transfer: ${local_path} not found."
        fi
#    done
done

echo "------------------------------------------------"
echo "GFSv16 vs GFSv17 images were copied to emcrzdm." 
echo "Updating date in index.php file and copying..."
echo "------------------------------------------------"

# 6. Run the website date update script
/lfs/h2/emc/vpppg/save/alicia.bentley/gfs_realtime_maps/website/edit_website_date.sh ${start_date}${start_hh}
echo "Sleeping for 3 seconds..."
sleep 3

# 7. SCP the index.php to the web server
if [ ${plot_type} == "500Z" ]; then
    scp /lfs/h2/emc/vpppg/save/alicia.bentley/gfs_realtime_maps/website/index.php abentley@emcrzdm:/home/people/emc/www/htdocs/users/meg/gfsv17/realtime/.
fi

echo "------------------------------------------------"
echo "index.php update complete. All tasks finished."
echo "------------------------------------------------"
