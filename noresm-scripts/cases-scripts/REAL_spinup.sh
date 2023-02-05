#!/bin/bash

# Spin up simulation of REAL: 
# - semi-realistic vegetation shift (LPJGUESS data), 
# - AMIP simul (details in %NORPDDMSBC) with sectional scheme(%SEC), 
# - 30 years (starts in 2000)
# - no need for nudging (no %SDYN)

set -o errexit #like assert to check and quit program in case of error
set -o nounset

# Simulation specifics:
export CASENAME=REAL_2000_spinup_f19_f19
export SURFDATA_FILE='/cluster/home/adelez/noresm-inputdata/surfdata_map/surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304_GFDL.nc'
#–––––––––––––––––––––––––––––––––––––––––

export NORESM_ACCOUNT=nn8057k #NN8057K
export PROJECT=nn8057k
export NORESM_ROOT=/cluster/home/$USER/NorESM-sec
export NORESM_DATA=/cluster/shared/noresm/inputdata
export COMPSET=2000_CAM60%NORESM%SEC%NORPDDMSBC_CLM50%BGC-CROP_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV #SDYN
export RES=f19_f19


cd $NORESM_ROOT

#TAG=$(git describe)
CASEROOT=~/cases/$CASENAME #-$RES #$COMPSET-$RES-$CASE_NAME

rm -rf $CASEROOT #remove previous cases

cd cime/scripts
./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $NORESM_ACCOUNT --handle-preexisting-dirs r

cd $CASEROOT

# –––––––––––– Start simulation in: ––––––––––––
./xmlchange RUN_STARTDATE=2000-01-01
# –––––––––––– Generate restart files every: ––––––––––––
./xmlchange REST_OPTION=nyears
./xmlchange REST_N=1 #Produce restart files every REST_N=1 years (or the RESTART_OPTION)
# –––––––––––– Duration of simulation: ––––––––––––
./xmlchange STOP_OPTION=nyears
./xmlchange STOP_N=5 #30 years
#./xmlchange CONTINUE_RUN=TRUE
./xmlchange RESUBMIT=5 #After first submit, redo it for 5 times 5ys+5x5ys=30ys
# It is better to devide this long simulation in smaller time series
# –––––––––––– The machine wallclock setting: ––––––––––––
./xmlchange --subgroup case.run JOB_WALLCLOCK_TIME=24:00:00
# –––––––––––– For nudging: ––––––––––––
./xmlchange CALENDAR=GREGORIAN # Keep it in the spinup run to avoid unmatching calendar problem
#./xmlchange CAM_CONFIG_OPTS=-offline_dyn #If nudging, but compset is not set SDYN 



#./case.build --clean
./case.setup

# Ensure that the land initial file is the same in all runs (just en extra check, not essential)
echo -e "&clm_inparm\n finidat = '/cluster/shared/noresm/inputdata/lnd/clm2/initdata_map/clmi.BHIST.2000-01-01.0.9x1.25_gx1v7_simyr2000_c181015.nc'">> user_nl_clm
# Modified idealized surfdata file
echo -e " fsurdat = ${SURFDATA_FILE}">> user_nl_clm
# Ensure intrpolation true for initial file and surfdata file
echo -e " use_init_interp = .true.">> user_nl_clm

# NO Nudging ERA-Interrim
# NO Aerosol diagnostic and decomposition
# NO Output in history files

./case.build
./case.submit

