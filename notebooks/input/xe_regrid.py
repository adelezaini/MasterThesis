#!/usr/bin/python

###### This python script is needed in case the current environment conflicts with xesmf installation
import numpy as np
import xarray as xr
import sys; sys.path.append("..")
from regrid import regrid

"""Usage:
  conda activate xesmf_env
  python3 xe_regrid.py pfts_LPJGUESS.nc pfts_CLM.nc ../../processed-data/input/IDEALIZED/
  conda activate base
"""

def main(file_in, file_target, path, file_out = 'regridded_dataset.nc', method = 'bilinear', mask=True):
    dset_in = xr.open_dataset(path+file_in)
    dset_target = xr.open_dataset(path+file_target)
    print("File imported")
    
    dset_out = regrid(dset_in, dset_target, method, mask)
    print("Regrid done")
    dset_out.load().to_netcdf(path+file_out)
    print("File saved")
         
if __name__ == '__main__':
    import sys

    args = sys.argv
    main(*args[1:])
