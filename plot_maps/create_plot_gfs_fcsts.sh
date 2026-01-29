#!/bin/bash
##############################################
# Script for submitting jobs on WCOSS2
# that plot forecast maps and analyses
##############################################

echo output path: ${OUTPUT_PATH}

INITDATE=$1
CYC=$2
FHR=$3
echo ${INITDATE} ${CYC} ${FHR}

mkdir -p ${OUTPUT_PATH}
mkdir -p ${MAP_PATH}/gfs/${INITDATE}${CYC}/scripts

#################################################################################################
#-----------------------------------------------------------------------------------------
# Creating a job to plot GFS forecasts for a particular initialization date and cycle
#-----------------------------------------------------------------------------------------

cat > ${MAP_PATH}/gfs/${INITDATE}${CYC}/scripts/plot_gfs_slp_3panel.py <<EOF
#!/bin/bash
#PBS -N gfs_f${FHR}_plot
#PBS -o ${OUTPUT_PATH}/out_plot_gfs_slp_${INITDATE}${CYC}_f${FHR}.out
#PBS -e ${OUTPUT_PATH}/out_plot_gfs_slp_${INITDATE}${CYC}_f${FHR}.err
#PBS -l select=1:ncpus=1:mem=20GB
#PBS -q dev
#PBS -l walltime=00:10:00
#PBS -A VERF-DEV

module load prod_envir/2.0.6
module load intel/19.1.3.304
module load python/3.8.6
module use /lfs/h1/mdl/nbm/save/apps/modulefiles
module load python-modules/3.8.6
export PYTHONPATH="${PYTHONPATH}:/lfs/h2/emc/lam/noscrub/Benjamin.Blake/python"
module load proj/7.1.0
module load geos/3.8.1
module load libjpeg-turbo/2.1.0
module load imagemagick/7.0.8-7
module load wgrib2/2.0.8_wmo
module load libjpeg/9c
module load grib_util/1.2.4

cd ${MAP_PATH}/gfs/${INITDATE}${CYC}/scripts
cp ${SCRIPTS_PATH}/plot_gfs_slp_3panel.py .

	export FHHH=${FHR}

        #/bin/rm -rf ${MAP_PATH}/gfs/${INITDATE}${CYC}/gfs_*_slp_${CASE}_${COUNTER}.png

	python plot_gfs_slp_3panel.py ${INITDATE} ${CYC} ${FHR} ${DOMAIN_ARRAY} ${DATA_PATH} ${CASE}
        sleep 3

#mv gfs_*_slp_${CASE}_*.png ${MAP_PATH}/gfs/${INITDAT}${CYC}/.

exit

EOF

#----------------------------------------------------------------------------------------

qsub ${MAP_PATH}/gfs/${INITDATE}${CYC}/scripts/plot_gfs_slp_3panel.py
sleep 3

#----------------------------------------------------------------------------------------

exit

