########## Code inspired by Astrid BG ############
import numpy as np
import netCDF4
import pandas as pd
import xarray as xr
import glob #return all file paths that match a specific pattern
import matplotlib as mpl
import matplotlib.pyplot as plt

import sys; sys.path.append("..")
from dataset_manipulation import fix_cam_time

"""
Example usage:
python3 postprocess.py casename casealias h2

python3 postprocess.py VEG_SHIFT_IDEAL_2000_sec_nudg_f19_f19 IDEAL-ON h1
"""

raw_path = '../../../archive/' #Betzy: /cluster/home/adelez/nird/ #Nird: /nird/home/adelez/storage/
processed_path = '../../processed-data/output/'

def main(casename, casealias, history_field='h0'):#, startyear, endyear, var,history_field='h2',postfix='',path=path_to_noresm_archive, output_path=outpath_default):
         
    fp = raw_path+casename+'/atm/hist/'+casename+'.cam.h0.*.nc' #VEG_SHIFT_IDEAL_2000_sec_nudg_f19_f19.cam.h0.2007-01.nc
    all_files = glob.glob(fp)
    all_files.sort()
    print("Files found")

    ds = xr.open_mfdataset(all_files)
    print("Dataset created")

    #-----------------------------
    # Postprocessing of model data
    #-----------------------------

    # Fix timestamp of model data
    ds = fix_cam_time(ds)

    # Remove spinup months of data set
    ds = ds.isel(time=slice(12,len(ds.time)))

    print("Postprocessing completed")

    #--------------------------------------------------------------------
    # Store relevant variables intermediately to save time when plotting,
    # change to desired units and create combined variables
    #--------------------------------------------------------------------
    date = '20082012'

    # BVOC variables
    variables = ['SFisoprene', 'SFmonoterp']
    ds[variables].to_netcdf(processed_path+casealias+'_'+'BVOC_'+date+'.nc')
    # SOA variables
    variables = ['N_AER', 'SOA_A1','SOA_NA','cb_SOA_A1','cb_SOA_NA', 'cb_SOA_A1_OCW', 'cb_SOA_NA_OCW']
    ds[variables].to_netcdf(processed_path+casealias+'_'+'SOA_'+date+'.nc')
    # CLOUD PROPERTIES
    variables = ['ACTNL', 'ACTREL','CDNUMC', 'CLDHGH', 'CLDLOW', 'CLDMED', 'CLDTOT', 'CLDLIQ', 'CLOUD', 'CLOUDCOVER_CLUBB', 'FCTL', 'LWCF', 'SWCF', 'NUMLIQ', 'TGCLDLWP']
    ds[variables].to_netcdf(processed_path+casealias+'_'+'CLOUDPROP_'+date+'.nc')
    # RADIATIVE COMPONENTS
    variables = ['FLNT', 'FSNT', 'FLNT_DRF', 'FLNTCDRF', 'FSNTCDRF', 'FSNT_DRF', 'LHFLX', 'OMEGAT', 'SHFLX']
    ds[variables].to_netcdf(processed_path+casealias+'_'+'RADIATIVE_'+date+'.nc')
    # TURBULENT FLUXES
    variables = ['LHFLX', 'OMEGAT', 'SHFLX']
    ds[variables].to_netcdf(processed_path+casealias+'_'+'TURBFLUXES_'+date+'.nc')
    
    
    """
                if 'SW_rest_Ghan' == var:
                    varnames_mod = varnames_mod + ['FSNTCDRF']
                if 'LW_rest_Ghan' == var:
                    varnames_mod = varnames_mod + ['FLNTCDRF']
                if 'DIR_Ghan' == var:
                    varnames_mod = varnames_mod + ['FSNT_DRF', 'FSNT', 'FLNT_DRF', 'FLNT']
                if 'SWDIR_Ghan' == var:
                    varnames_mod = varnames_mod + ['FSNT_DRF', 'FSNT']
                if 'LWDIR_Ghan' == var:
                    varnames_mod = varnames_mod + ['FLNT_DRF', 'FLNT']
                if 'SWCF_Ghan' == var:
                    varnames_mod = varnames_mod + ['FSNT_DRF', 'FSNTCDRF']
                elif var == 'LWCF_Ghan':
                    varnames_mod = varnames_mod + ['FLNT_DRF', 'FLNTCDRF']
                elif var == 'NCFT_Ghan':
                    varnames_mod = varnames_mod + ['FSNT_DRF', 'FSNTCDRF'] + ['FLNT_DRF', 'FLNTCDRF']
    """

"""
rpath="/projects/NS9600K/astridbg/data/model/noresm_rawdata/cases/"
wpath="/projects/NS9600K/astridbg/data/model/noresm_postprocessed/"

#case = "def_20210126"
case = "meyers92_20220210"
#case = "andenes21_20220222"
casefolder="NF2000climo_f19_tn14_"+case

all_files = glob.glob(rpath+casefolder+"/atm/hist/"+casefolder+".cam.h0.*")
all_files.sort()
print("Files found")

ds = xr.open_mfdataset(all_files)
print("Dataset created")

#-----------------------------
# Postprocessing of model data
#-----------------------------

# Fix timestamp of model data
ds = functions.fix_cam_time(ds)

# Remove spinup months of data set
ds = ds.isel(time=slice(3,len(ds.time)))

#-----------------------------

print("Postprocessing completed")

#--------------------------------------------------------------------
# Store relevant variables intermediately to save time when plotting,
# change to desired units and create combined variables
#--------------------------------------------------------------------
date = "2007-04-15_2010-03-15"

# For cases meyers92 and andenes21
#variables = ["NIMEY","AWNI", "FREQI","CLDICE","SWCF","LWCF","LWCFS","SWCFS","NETCFS","AWNICC","CLDTOT","CLDHGH","CLDMED","CLDLOW","TGCLDIWP","TGCLDLWP","TREFHT"]

# For case def
#variables = ["AWNI", "FREQI","CLDICE","SWCF","LWCF","LWCFS","SWCFS","NETCFS","AWNICC","TH","CLDTOT","CLDHGH","CLDMED","CLDLOW","TGCLDIWP","TGCLDLWP","TREFHT"]

variables = ['SFisoprene', 'SFmonoterp']


for var in variables:
    print("Started writing variable:")
  
    # Change to desired units
    if var == "NIMEY" or var == "AWNI":
        ds[var].values = ds[var].values*1e-3 # Change unit to number per litre and name
        ds[var].attrs["units"] = "1/L"

    if var == "T" or var == "TREFHT" or var=="TH":
        ds[var].values = ds[var].values - 273.15 # Change unit to degrees Celsius
        ds[var].attrs["units"] = r"$^{\circ}$C"

    if var == "CLDICE" or var == "CLDLIQ" or var == "Q" or var == "ICIMR" or var == "ICWMR":
        ds[var].values = ds[var].values*1e+3 # Change unit to grams per kilograms
        ds[var].attrs["units"] = "g/kg"
  
    if var == "TGCLDIWP" or var == "TGCLDLWP":
        ds[var].values = ds[var].values*1e+3 # Change unit to grams per squared meter
        ds[var].attrs["units"] = "g/m$^2$"

    if var == "IWC":
        ds[var].values = ds[var].values*1e+3 # Change unit to grams per cubic meter
        ds[var].attrs["units"] = "g/m$^3$"

    # Change to more meaningful name

    if var == "TREFHT":
        ds[var].attrs["long_name"] = "Surface (2m) Temperature"
    if var == "NIMEY":
        ds[var].attrs["long_name"] = "Activated Ice Number Concentation due to Meyers' parameterisation"
    if var == "AWNI":
        ds[var].attrs["long_name"] = "Average cloud ice number concentration"
    if var == "ICIMR":
        ds[var].attrs["long_name"] = "In-cloud ice mixing ratio"
    if var == "ICWMR":
        ds[var].attrs["long_name"] = "In-cloud liquid water mixing ratio"

    # Make combined data variables
    if var == "LWCFS":
        ds = ds.assign(LWCFS=ds["FLNSC"]-ds["FLNS"])
        ds[var].attrs["units"] = "W/m$^2$"
        ds[var].attrs["long_name"] = "Longwave cloud radiative effect at surface"

    if var == "SWCFS":
        ds = ds.assign(SWCFS=ds["FSNS"]-ds["FSNSC"])
        ds[var].attrs["units"] = "W/m$^2$"
        ds[var].attrs["long_name"] = "Shortwave cloud radiative effect at surface"
  
    if var == "AWNICC":
        ds = ds.assign(AWNICC=ds["AWNI"]/ds["FREQI"].where(ds["FREQI"]>0))
        ds[var] = ds[var].fillna(0)
        ds[var].values = ds[var].values*1e-3 # Change unit to number per litre
        ds[var].attrs["units"] = "1/L"
        ds[var].attrs["long_name"] = "Average cloud ice number concentration in cold clouds"
        
    if var == "NETCFS":
        ds = ds.assign(NETCFS=ds["FSNS"]-ds["FSNSC"]-ds["FLNS"]-(-ds["FLNSC"]))
        ds[var].attrs["units"] = "W/m$^2$"
        ds[var].attrs["long_name"] = "Net cloud radiative effect at surface"
    
    if var == "CLDLWEM":
        ds = ds.assign(CLDLWEM=1-np.exp(-0.13*ds["TGCLDLWP"]*1e+3))
        ds[var].attrs["units"] = "Emissivity"
        ds[var].attrs["long_name"] = "Cloud Longwave Emissivity"

    if var == "CLDLWEMS":
        ds = ds.assign(CLDLWEMS=1-np.exp(-0.158*ds["TGCLDLWP"]*1e+3))
        ds[var].attrs["units"] = "Emissivity"
        ds[var].attrs["long_name"] = "Cloud Longwave Emissivity"

    print(ds[var].attrs["long_name"])
    print("Units: ", ds[var].attrs["units"])
  
    ds[var].to_netcdf(wpath+var+"_"+case+"_"+date+".nc")
"""
if __name__ == '__main__':
    import sys

    args = sys.argv
    main(*args[1:])
