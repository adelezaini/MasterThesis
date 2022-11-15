###### This python file collects fuctions to make some plotting with LPJGUESS

####### Import packages (to clean
import numpy as np
import netCDF4 as nc
import xarray as xr
xr.set_options(display_style='html')
import pandas as pd
import os
from scipy.optimize import curve_fit
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import transforms
from matplotlib.colors import ListedColormap
from matplotlib.image import imread
import matplotlib.path as mpath
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import proplot as pplt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker
from cartopy.util import add_cyclic_point
from owslib.wms import WebMapService


#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
