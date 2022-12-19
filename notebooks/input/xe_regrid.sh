#!/bin/bash

conda activate xesmf_env
printf 'conda activate xesmf_env'
python3 xe_regrid.py pfts_LPJGUESS.nc pfts_CLM_sel.nc ../../processed-data/input/IDEALIZED/ pfts_LPJGUESS_regridded.nc
conda activate base
