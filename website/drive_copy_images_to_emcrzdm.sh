#!/bin/bash
###################################################
# Script to plot GFS forecast map comparisons
#
# Contributors: Alicia.Bentley@noaa.gov
# NOAA/NWS/NCEP/Environmental Modeling Center
###################################################
module reset
module load prod_envir/2.0.6
module load intel/19.1.3.304
module load python/3.8.6
module use /lfs/h1/mdl/nbm/save/apps/modulefiles
module load python-modules/3.8.6
export PYTHONPATH="${PYTHONPATH}:/lfs/h2/emc/vpppg/noscrub/Alicia.Bentley/python"
module load proj/7.1.0
module load geos/3.8.1
module load libjpeg-turbo/2.1.0
module load imagemagick/7.0.8-7
module load wgrib2/2.0.8_wmo
module load libjpeg/9c
module load grib_util/1.2.4

cyc=$1
echo "cyc: ${cyc}"

#Logic to determine holddate.txt based $cyc (00, 06, 12, 18)
if [ "$cyc" -ge 18 ]; then
    yyyymmdd=$(/bin/date --date="yesterday" +%Y%m%d)
else
    yyyymmdd=$(/bin/date +%Y%m%d)
fi

sleep 1
echo $yyyymmdd$cyc

export SCRIPTS_PATH='/lfs/h2/emc/vpppg/save/'${USER}'/gfs_realtime_maps/website'

#===============================================================================================================
#==============================================  BEGIN CHANGES  ================================================
#===============================================================================================================

# Specify the plot types that will be copied from WCOSS2 to emcrzdm (e.g., 500Z, mslp, 850T)
for plot_type in 500Z mslp 850T; do

    echo "Kicking off script to copy ${plot_type} images from WCOSS2 to emcrzdm for $yyyymmdd$cyc"
    
    # Adding '&' at the end sends this to the background
    ${SCRIPTS_PATH}/copy_images_to_emcrzdm.sh ${yyyymmdd} ${cyc} ${plot_type} > /lfs/h2/emc/ptmp/alicia.bentley/cron.out/copy_${plot_type}_to_emcrzdm.out 2>&1 &
    
    # Optional: Keep a tiny sleep if the server dislikes 3 instant hits
    sleep 1

done

# Wait for all background processes to finish before exiting the main script
# wait

echo "All image transfers have been initiated."

exit
