#!/bin/bash
##############################################
# Script for submitting jobs on WCOSS2
# that plot forecast maps and analyses
##############################################

echo output path: ${OUTPUT_PATH}

INITDATE=$1
CYC=$2
DOMAIN=$3
echo ${INITDATE} ${CYC} ${DOMAIN}

mkdir -p ${OUTPUT_PATH}
#mkdir -p ${MAP_PATH}/gfs/${INITDATE}${CYC}/scripts
mkdir -p ${MAP_PATH}/gfs/${INITDATE}${CYC}/mslp
mkdir -p ${MAP_PATH}/gfs/${INITDATE}${CYC}/500Z

#################################################################################################
#-----------------------------------------------------------------------------------------
# Creating a job to plot MSLP (part 1) GFS forecasts for a particular init. date and cycle
#-----------------------------------------------------------------------------------------

cat > ${MAP_PATH}/gfs/${INITDATE}${CYC}/mslp/kickoff_plot_gfs_mslp_3panel_part1.py <<EOF
#!/bin/bash
#PBS -N gfs_mslp_plot
#PBS -o ${OUTPUT_PATH}/out_plot_gfs_mslp_part1_${INITDATE}${CYC}.out
#PBS -e ${OUTPUT_PATH}/out_plot_gfs_mslp_part1_${INITDATE}${CYC}.err
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

cd ${MAP_PATH}/gfs/${INITDATE}${CYC}/mslp
cp ${SCRIPTS_PATH}/plot_gfs_mslp_3panel_part1.py .

	#export FHHH=${FHR}

	python plot_gfs_mslp_3panel_part1.py ${INITDATE} ${CYC} ${DOMAIN}
        sleep 3

exit

EOF

#----------------------------------------------------------------------------------------

qsub ${MAP_PATH}/gfs/${INITDATE}${CYC}/mslp/kickoff_plot_gfs_mslp_3panel_part1.py
sleep 3
echo Submitted mslp plots part1 job! 

#----------------------------------------------------------------------------------------

#################################################################################################
#-----------------------------------------------------------------------------------------
# Creating a job to plot MSLP (part 2) GFS forecasts for a particular init. date and cycle
#-----------------------------------------------------------------------------------------

cat > ${MAP_PATH}/gfs/${INITDATE}${CYC}/mslp/kickoff_plot_gfs_mslp_3panel_part2.py <<EOF
#!/bin/bash
#PBS -N gfs_mslp_plot
#PBS -o ${OUTPUT_PATH}/out_plot_gfs_mslp_part2_${INITDATE}${CYC}.out
#PBS -e ${OUTPUT_PATH}/out_plot_gfs_mslp_part2_${INITDATE}${CYC}.err
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

cd ${MAP_PATH}/gfs/${INITDATE}${CYC}/mslp
cp ${SCRIPTS_PATH}/plot_gfs_mslp_3panel_part2.py .

        #export FHHH=${FHR}

        python plot_gfs_mslp_3panel_part2.py ${INITDATE} ${CYC} ${DOMAIN}
        sleep 3

exit

EOF

#----------------------------------------------------------------------------------------

qsub ${MAP_PATH}/gfs/${INITDATE}${CYC}/mslp/kickoff_plot_gfs_mslp_3panel_part2.py
sleep 3
echo Submitted mslp plots part2 job! 

#----------------------------------------------------------------------------------------

#################################################################################################
#-----------------------------------------------------------------------------------------
# Creating a job to plot 500Z GFS forecasts for a particular init. date and cycle
#-----------------------------------------------------------------------------------------

cat > ${MAP_PATH}/gfs/${INITDATE}${CYC}/500Z/kickoff_plot_gfs_500Z_3panel.py <<EOF
#!/bin/bash
#PBS -N gfs_500Z_plot
#PBS -o ${OUTPUT_PATH}/out_plot_gfs_500Z_${INITDATE}${CYC}.out
#PBS -e ${OUTPUT_PATH}/out_plot_gfs_500Z_${INITDATE}${CYC}.err
#PBS -l select=1:ncpus=1:mem=200GB
#PBS -q dev
#PBS -l walltime=00:40:00
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

cd ${MAP_PATH}/gfs/${INITDATE}${CYC}/500Z
cp ${SCRIPTS_PATH}/plot_gfs_500Z_3panel.py .

        #export FHHH=${FHR}

        python plot_gfs_500Z_3panel.py ${INITDATE} ${CYC} ${DOMAIN}
        sleep 3

#mv image_*.png ${MAP_PATH}/gfs/${INITDATE}${CYC}/500Z/.

exit

EOF

#----------------------------------------------------------------------------------------

qsub ${MAP_PATH}/gfs/${INITDATE}${CYC}/500Z/kickoff_plot_gfs_500Z_3panel.py
sleep 3
echo Submitted 500Z plots job!

#----------------------------------------------------------------------------------------

exit

