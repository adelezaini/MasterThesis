#!/bin/bash

# CTRL case: 
# - no vegetation shift, 
# - AMIP simul (details in %NORPDDMSBC) with sectional scheme(%SEC) and nudging (%SDYN)
# - 7 years (starts in 2007, matching the nudging)

set -o errexit #like assert to check and quit program in case of error
set -o nounset

# Simulation specifics:
export CASENAME=CTRL_2000_f19_f19
export SPINUP_CASENAME=CTRL_2000_spinup_f19_f19
#–––––––––––––––––––––––––––––––––––––––––

export NORESM_ACCOUNT=nn8057k #NN8057K
export PROJECT=nn8057k
export NORESM_ROOT=/cluster/home/$USER/NorESM-sec
export NORESM_DATA=/cluster/shared/noresm/inputdata
export COMPSET=2000_CAM60%NORESM%SEC%NORPDDMSBC%SDYN_CLM50%BGC-CROP_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV
export RES=f19_f19
#–––––––––––For spin up
export RESTART_SPINUP_DIR=~/work/archive/$SPINUP_CASENAME/rest/0031-01-01-00000 #work -> /cluster/work/users/adelez
export RESTART_DIR=~/noresm-inputdata/restart-cases/$CASENAME #noresm-inputdata -> /cluster/projects/nn8057k/adelez/noresm-inputdata

cd $NORESM_ROOT

#TAG=$(git describe)
CASEROOT=~/cases/$CASENAME #-$RES #$COMPSET-$RES-$CASE_NAME

rm -rf $CASEROOT #remove previous cases

cd cime/scripts
./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $NORESM_ACCOUNT --handle-preexisting-dirs r

cd $CASEROOT

#–––––––––––––– Restart from spinup
# 1. move data from work/archive/spinup-casename/rest to noresm-inpudata and unzip it
mkdir -p $RESTART_DIR
rsync -avz $RESTART_SPINUP_DIR/* $RESTART_DIR/
gunzip $RESTART_DIR/*.gz
