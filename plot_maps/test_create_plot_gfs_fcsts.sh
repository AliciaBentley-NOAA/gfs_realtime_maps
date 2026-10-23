#!/bin/bash
##############################################
# Script for submitting jobs on WCOSS2
# that plot forecast maps and analyses
##############################################

echo output path: ${OUTPUT_PATH}

INITDATE=$1
CYC=$2
DOMAIN=$3
DATA_PATH=$4
echo ${INITDATE} ${CYC} ${DOMAIN} ${DATA_PATH}

mkdir -p ${OUTPUT_PATH}
mkdir -p ${MAP_PATH}/gfs/${INITDATE}${CYC}/${DOMAIN}/htsgw

#################################################################################################
#-----------------------------------------------------------------------------------------
# Creating a job to plot htsgw GFS forecasts for a particular init. date and cycle
#-----------------------------------------------------------------------------------------

cat > ${MAP_PATH}/gfs/${INITDATE}${CYC}/${DOMAIN}/htsgw/kickoff_plot_gfs_htsgw_3panel.py <<EOF
#!/bin/bash
#PBS -N gfs_htsgw_plot
#PBS -o ${OUTPUT_PATH}/out_plot_gfs_htsgw_${INITDATE}${CYC}.out
#PBS -e ${OUTPUT_PATH}/out_plot_gfs_htsgw_${INITDATE}${CYC}.err
#PBS -l select=1:ncpus=1:mem=100GB
#PBS -q dev
#PBS -l walltime=00:50:00
#PBS -A VERF-DEV

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

cd ${MAP_PATH}/gfs/${INITDATE}${CYC}/${DOMAIN}/htsgw
cp ${SCRIPTS_PATH}/plot_gfs_htsgw_3panel.py .

        #export FHHH=${FHR}

        python plot_gfs_htsgw_3panel.py ${INITDATE} ${CYC} ${DOMAIN} ${DATA_PATH}
        sleep 3

exit

EOF

#----------------------------------------------------------------------------------------

qsub ${MAP_PATH}/gfs/${INITDATE}${CYC}/${DOMAIN}/htsgw/kickoff_plot_gfs_htsgw_3panel.py
sleep 3
echo Submitted htsgw plots job! 

#----------------------------------------------------------------------------------------

#################################################################################################

exit

