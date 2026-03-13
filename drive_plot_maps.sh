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

######Logic to determine holddate.txt based $cyc (00, 06, 12, 18)
if [ "$cyc" -ge 18 ]; then
    /bin/date --date="yesterday" +%Y%m%d > holddate.txt
else
    /bin/date +%Y%m%d > holddate.txt
fi

sleep 1
year=`cut -c 1-4 holddate.txt`
month=`cut -c 5-6 holddate.txt`
day=`cut -c 7-8 holddate.txt`
export longdate=${year}${month}${day}
echo $longdate$cyc


#===============================================================================================================
#==============================================  BEGIN CHANGES  ================================================
#===============================================================================================================

# ********************************************
# ****Specify case name and data/map paths****
# ********************************************
# Specify case study name (e.g., dorian2019)
export CASE='realtime'

# Location of your saved GFS/GEFS evaluation /plot_maps directory
export SCRIPTS_PATH='/lfs/h2/emc/vpppg/save/'${USER}'/gfs_realtime_maps/plot_maps'

# Location of downloaded forecast/analysis files
#export DATA_PATH='/lfs/h2/emc/gfstemp/emc.global/comroot/retrov17_01_realtime/'

# Location to plot maps
export MAP_PATH='/lfs/h2/emc/vpppg/noscrub/'${USER}'/gfs_realtime_maps/maps'

# Location to write output from submitted plot_maps jobs
export OUTPUT_PATH=${MAP_PATH}'/output'

# *************************************************************
# ****Specify which models to plot, forecast hours, domains****
# *************************************************************
# Select which models to plot (YES/NO)
export PLOT_GFS_FCSTS=YES

# Specify the domains to plot. This must be written as: 'domain1,domain2,...' (with no spaces)
# Example input: 'conus,northeast'
export DOMAIN_ARRAY='conus'

# Specify the forecast hours (HHH format) to plot (typically every 6 hours from F000 to F240
#for fhr in 078
#do

#===============================================================================================================        
#===============================================  END CHANGES  =================================================
#===============================================================================================================

if [ $PLOT_GFS_FCSTS = YES ]; then
        echo "Create/submit scripts to plot real-time GFS forecasts (Init.: ${longdate}${cyc} for ${DOMAIN_ARRAY})"
        ${SCRIPTS_PATH}/create_plot_gfs_fcsts.sh $longdate $cyc $DOMAIN_ARRAY
        sleep 2
fi

#done

exit
