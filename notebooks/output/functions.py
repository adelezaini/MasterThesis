import numpy as np
import xarray as xr

import sys; sys.path.append("..")
from dataset_manipulation import *

casealias = ['CTRL', 'IDEAL-ON', 'IDEAL-OFF', 'REAL-ON', 'REAL-OFF']

def load_dataset_dict(variable, cases=casealias, boreal_lat=45.):
    processed_path = '../../processed-data/postprocessing/' #/Users/adelezaini/Desktop/master-thesis/processed-data/output/IDEAL-ON_BVOC_20082012.nc
    date = '20082012'
    ds_dict = {}
    for case in cases:
        ds = xr.open_dataset(processed_path+case+'_'+variable+'_'+date+'.nc')
        ds = convert360_180(ds)
        #ds_dict[case] = ds.where(ds.LANDFRAC.mean('time')>0.)
        ds_dict[case]= ds.where(ds.lat>boreal_lat, drop=True)
    return ds_dict


def fix_names_soa(ds):
    """Assign clearer and more meaningful names"""
    
    ds_ = ds.copy(deep=True)
    
    for var in list(ds_.keys()):
        
        if var == "SOA_A1":
            ds_[var].attrs["long_name"] = "SOA_A1 concentration"
        elif var == "SOA_NA":
            ds_[var].attrs["long_name"] = "SOA_NA concentration"
        elif var == "cb_SOA_A1":
            ds_[var].attrs["long_name"] = "SOA_A1 burden column"
        elif var == "cb_SOA_NA":
            ds_[var].attrs["long_name"] = "SOA_NA burden column"
        elif var == "cb_SOA_A1_OCW":
            ds_[var].attrs["long_name"] = "SOA_A1 burden column in cloud water"
        elif var == "cb_SOA_NA_OCW":
            ds_[var].attrs["long_name"] = "SOA_NA burden column in cloud water"
        
        else:
            continue
    return ds_

def fix_soa(ds):
    """ Convert some units to have a more meaningful representation """
    
    ds_ = ds.copy(deep=True)
    
    for var in list(ds_.keys()):
            
        if var == "N_AER":
            ds_[var].attrs["units"] = "cm$^{-3}$" # Set unit to cm-3
        else:
            continue
        return ds_
        
def add_SOA_TOT(ds, casealias):
    ds_ = ds
    for case in casealias:
        ds_[case] = fix_soa(fix_names_soa(ds_[case]))
        ds_[case]['cb_SOA_TOT'] = ds_[case]['cb_SOA_NA'] + ds_[case]['cb_SOA_A1']
        ds_[case]['cb_SOA_TOT'].attrs['long_name'] = "total SOA burden column"
        ds_[case]['SOA_TOT'] = ds_[case]['SOA_NA'] + ds_[case]['SOA_A1']
        ds_[case]['SOA_TOT'].attrs['long_name'] = "total SOA concentration"
    return ds_
    
def fix_cloud(ds):
    
    ds_ = ds.copy(deep=True)
    
    for var in list(ds_.keys()):
            
        if var == "ACTNL":
            ds_[var].values = ds_[var].values*1e-12
        if var == "ACTREL":
            ds_[var].attrs['units'] = "$\mu$m"
        else:
            continue
        return ds_
        
def fix_radiative_names(ds):

    ds_ = ds.copy(deep=True)
    
    ds_ = aerosol_cloud_forcing_scomposition_Ghan(ds_)

    for var in ['SWDIR', 'LWDIR', 'DIR', 'SWCF', 'LWCF', 'NCFT', 'SW_rest', 'LW_rest', 'FREST', 'FTOT']:
            
        
        if 'SWDIR' == var:
            ds_[var].attrs['long_name'] = "Shortwave aerosol direct radiative forcing"
        elif 'LWDIR' == var:
            ds_[var].attrs['long_name'] = "Longwave aerosol direct radiative forcing"
        elif 'DIR' == var:
            ds_[var].attrs['long_name'] = "Net aerosol direct radiative forcing"
        elif 'SWCF' == var:
            ds_[var].attrs['long_name'] = "Shortwave cloud radiative forcing"
        elif 'LWCF' == var:
            ds_[var].attrs['long_name'] = "Longwave cloud radiative forcing"
        elif 'NCFT' == var:
            ds_[var].attrs['long_name'] = "Net cloud radiative forcing"
        elif 'SW_rest' == var:
            ds_[var].attrs['long_name'] = "Shortwave surface change radiative forcing"
        elif 'LW_rest' == var:
            ds_[var].attrs['long_name'] = "Longwave surface change radiative forcing"
        elif 'SWTOT' == var:
            ds_[var].attrs['long_name'] = "Shortwave radiative forcing at top of the model"
        elif 'LWTOT' == var:
            ds_[var].attrs['long_name'] = "Longwave radiative forcing at top of the model"
        elif 'FREST' == var:
            #ds_[var] = ds_['FSNTCDRF'] - ds_['FLNTCDRF']
            #ds_[var].attrs['units'] = ds_['FSNTCDRF'].attrs['units']
            ds_[var].attrs['long_name'] = "Net surface change radiative forcing"
        elif 'FTOT' == var:
            #ds_[var] = ds_['FSNT'] - ds_['FLNT']
            #ds_[var].attrs['units'] = ds_['FLNT'].attrs['units']
            ds_[var].attrs['long_name'] = "Net radiative forcing at top of the model"""
    return ds_

def fix_et(ds):
    ds_ = ds
    for case in casealias:
        ds_[case]['QFLX_EVAP_TOT'].attrs['long_name'] = 'total veg and soil evapotranspiration'
        ds_[case]['QSOIL'] = ds_[case]['QSOIL']*60*60*24
        ds_[case]['QSOIL'].attrs['units'] = 'mm/day'
        ds_[case]['QFLX_EVAP'] = ds_[case]['QFLX_EVAP_TOT']
        ds_[case]['QFLX_EVAP'] = ds_[case]['QFLX_EVAP_TOT'] - ds_[case]['QSOIL']
        ds_[case]['QFLX_EVAP'].attrs['long_name'] = 'evapotraspiration from vegetation'
    return ds_
