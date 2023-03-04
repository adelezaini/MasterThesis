# Script to create BVOC input files for IDEAL and REAL runs from the output of the CTRL run
# based on Sara Marie Blichner's script: create_em_files_high_res.py

# Mount nird
#sshfs adelez@nird.sigma2.no:storage/ storage/
#Python environment
source pyenv/bin/activate
#Load module
module load NCO/5.0.3-intel-2021b

#Example usage: 
#python create_em_files_high_res.py case_name 2015 2018 SFisoprene h2 /proj/bolinc/users/x_sarbl/noresm_archive /proj/bolinc/users/x_sarbl/noresm_input_data 


export CTRL_CASENAME=CTRL_2000_f19_f19
export ARCHIVE_DIR='/cluster/home/adelez/storage/archive'
export TARGET_DIR='/cluster/home/adelez/noresm-inputdata/BVOCfromCTRL'

# Create emissions file for SFisoprene
python3 create_em_files_high_res.py $CTRL_CASENAME 2007 2012 SFisoprene h1 #$ARCHIVE_DIR $TARGET_DIR
# Create emissions file for SFmonoterp
python3 create_em_files_high_res.py $CTRL_CASENAME 2007 2012 SFmonoterp h1 #$ARCHIVE_DIR $TARGET_DIR
#
# Remove temporary files
#rm $TARGET_DIR/tmp_*.nc
#rm $TARGET_DIR/avg_*.nc
#rm $TARGET_DIR/ems_*SFisoprene.nc
#rm $TARGET_DIR/ems_*SFmonoterp.nc
