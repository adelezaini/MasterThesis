###### This python file collects fuctions to manipulate Xarray Dataset/DataArray

####### Import packages
import numpy as np
import netCDF4 as nc
import xarray as xr; xr.set_options(display_style='html')
import pandas as pd
import os
from scipy.special import erf


################ Operations over coordinates
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def convert360_180(ds):
    """Convert the longitude of the given xr:Dataset from [0-360] to [-180-180] deg"""
    _ds = ds.copy()
    if np.min(_ds['lon'].values) >= 0: # check if already
        attrs = _ds['lon'].attrs
        _ds.coords['lon'] = (_ds.coords['lon'] + 180) % 360 - 180
        _ds = _ds.sortby(_ds.lon)
        _ds['lon'].attrs = attrs
        _ds.lon.attrs['valid_max'] = 180.0
        _ds.lon.attrs['valid_min'] = -180.0
    return _ds
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def convert180_360(ds):
    """Convert the longitude of the given xr:Dataset from [-180-180] to [0-360] deg"""
    _ds = ds.copy()
    if np.min(_ds['lon'].values) <= 0: # check if already
        attrs = _ds['lon'].attrs
        _ds.coords['lon'] = _ds.coords['lon'] % 360
        _ds = _ds.sortby(_ds.lon)
        _ds['lon'].attrs = attrs
        _ds.lon.attrs['valid_max'] = 0.0
        _ds.lon.attrs['valid_min'] = 360.0
    return _ds
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def convert_lsmcoord(ds):
    """ When default coordinate are in Land Surface coord.
    Convert them in lon-lat. """
    
    _ds = ds.copy()
    #Set the longitude and latitude
    _ds['lsmlat'] = _ds['LATIXY'].isel(lsmlon=0) #or dset_in['lsmlat'] = dset_in['lat']
    _ds['lsmlon'] = _ds['LONGXY'].isel(lsmlat=0)
    #Rename coord
    _ds = _ds.rename({'lsmlat':'lat','lsmlon':'lon'})
    return _ds
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def convert_to_lsmcoord(ds):
    """ Convert lon-lat into Land Surface Model coordinates. """
    print("Allert convert_to_lsmcoord! Changing from coord to dim means loosing information and changing from values to indexes")
    _ds = ds.copy()
    _ds = _ds.rename({'lat':'lsmlat','lon':'lsmlon'})
    #From coordinate to dimensions (as original)
    _ds = _ds.drop_vars('lsmlat').drop_vars('lsmlon')

    return _ds
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def xr_prod_along_dim(ds, weights, dim):
    """
    Product along a specific dimension. Particularly suitable for weighting
    Edited code from https://www.reddit.com/r/learnpython/comments/g45f2u/multiplying_xarray_dataarrays/
    """
    
    assert ds[dim].size == weights[dim].size

    old_order = ds.dims
    new_order = tuple(list(set(old_order) - set([dim])) + [dim])

    ds_t = ds.transpose(*new_order)
    ds_weighted = ds_t * weights
    ds_weighted = ds_weighted.transpose(*old_order)

    return ds_weighted
    
    
################ Fitting in Xarray
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def polynomial_fit(ds, dim, deg=3):
    out = ds.polyfit(dim=dim, deg=deg, full=True)
    polyfit = xr.polyval(coord=ds[dim], coeffs=out.polyfit_coefficients).rename('polyfit')
    return polyfit

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def gaussian_fit(ds, dim, p0={'A':45, 'xc':55, 'sig':5}, asym_gauss=False, fixed_extremes=False):
    
    names=None
    
    def gaussian(x, A, xc, sig):
        return A*np.exp(-np.power((x - xc),2.) / (2 * np.power(sig,2.)))
    
    def asym_gaussian(x, *p):
        amp = (p[0] / (p[2] * np.sqrt(2 * np.pi)))
        spread = np.exp((-(x - p[1]) ** 2.0) / (2 * p[2] ** 2.0))
        skew = (1 + erf((p[3] * (x - p[1])) / (p[2] * np.sqrt(2))))
        return amp * spread * skew
    
    if asym_gauss:
        gaussian=asym_gaussian
        p0['p3']=1
        names=['A', 'xc', 'sig', 'p3']
        
    if fixed_extremes==True:
        sigma = np.ones(len(ds[dim].values))
        sigma[[0, -1]] = 0.01
        fit_params=ds.curvefit(coords=dim, func=gaussian, p0=p0, param_names=names, kwargs={'sigma': sigma})
    else:
        fit_params=ds.curvefit(coords=dim, func=gaussian, p0=p0, param_names=names)#, kwargs={'sigma': sigma})
    popt=fit_params.curvefit_coefficients # NO! .values
    gaussfit = gaussian(ds[dim], *popt.T).drop('param').rename('gaussfit')
    return gaussfit
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
