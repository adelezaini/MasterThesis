###### This python file collects fuctions to make some plotting

####### Import packages
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

################ Miscellaneous

def dict_to_legend(dct):
    return ["{} – {}".format(item, amount) for item, amount in dct.items()]


################ GridSpec: PlanteCaree Map with Lat_lon distributions

def map_lonlatdistribution(ds, lnd_frac, title, cbar_label=None, figsize=(10,6), cmap='Greens', color='g'):
    """
    Plot a map in PlateCaree projection with side Lat and Lon distribution.
    Distribution evaluated over the mean, considering the input as a percentage.
    
    Args:
    - ds (DataArray): PFT distribution with only dimensions lat-lon
    - lnd_frac (DataArray): land fraction - mandatory argument as a control
                            over the input dataset (0 over land, NaN over ocean)
    - *args: intuitive
    """
    if not cbar_label:
        cbar_label = ds.long_name
        
    ds = ds.copy()
    ds = ds.where(lnd_frac>0.)
        
    fig = plt.figure(figsize=figsize)
    grid = plt.GridSpec(4, 4, hspace=0.2, wspace=0.2, right=0.85)

    ####### Main map:
    main_ax = fig.add_subplot(grid[:-1, 1:], projection=ccrs.PlateCarree())
    main_ax.set_global()
    main_ax.coastlines()
    main_ax.set_aspect('auto')
    im = ds.plot(ax=main_ax, add_colorbar=False, cmap=cmap, vmin = 0, vmax =100)
    plt.suptitle(title, weight='bold', size='x-large', y=0.95)

    ####### Latitude plot:
    # It was hard to have an area but orientated vertically (hist has orientation, line is easy, area is hell)
    lat_ax = fig.add_subplot(grid[:-1, 0], sharey=main_ax, ylabel='Latitude [°]') #xticklabels=[],
    ### Rotate axis
    base = plt.gca().transData
    rot = transforms.Affine2D().rotate_deg(90)
    reflect_vertical = transforms.Affine2D(np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]]))

    ds_lat = ds.mean('lon').rename('Latitude [°]')
    ds_lat.to_series().rename_axis('').plot(kind='area', ax=plt.gca(),transform= reflect_vertical + rot + base, stacked=False, color=color,xlim=(0, ds_lat.max()+3), ylim=(-90,90))
    plt.gca().invert_xaxis() #same as lat_ax.invert_xaxis()

    ####### Longitude plot:
    lon_ax = fig.add_subplot(grid[-1, 1:], sharex=main_ax) #yticklabels=[],
    ds_lon = ds.mean('lat')
    ds_lon.to_series().rename_axis('Longitude [°]').plot(kind='area', ax=lon_ax, stacked=False, color=color, ylim=(0, ds_lon.max()+3))
    lon_ax.invert_yaxis()

    ####### Colorbar:
    axins = inset_axes(lon_ax, # here using axis of the lowest plot
               width="5%",  # width = 5% of parent_bbox width
               height="340%",  # height : 340% good for a (4x4) Grid
               loc='lower left',
               bbox_to_anchor=(1.05, 1.2, 1, 1),
               bbox_transform=lon_ax.transAxes,
               borderpad=0
               )

    cb = fig.colorbar(im, cax=axins,format='%.0f%%', label = cbar_label)

    plt.tight_layout()
    plt.show()
    
    
################ Boreal PFTs plot

def plot_boreal_pfts(boreal_pfts):
    """ Ah hoc plotting for the 5 boreal PFTs.
        Args:
        - boreal_pfts (DataArray): (lat, lon, natpft) with natpft = '2 - BoNET','3 - BoNDT','8 - BoBDT', '11 - BoBDS','12 - artic C3 grass'
    """
    
    titles=['2 - BoNET','3 - BoNDT','8 - BoBDT','11 - BoBDS','12 - artic C3 grass']
    #plt.tight_layout()
    p=boreal_pfts.plot.contourf(x='lon', y='lat', col='natpft', col_wrap=2,
                                  cmap='Greens', transform=ccrs.PlateCarree(),
                                  subplot_kws={'projection': ccrs.Orthographic(0, 90)},
                                  add_colorbar=False,figsize=(15, 15), robust=False)


    for i, ax in enumerate(p.axes.flat):
        ax_map_properties(ax, borders=False, rivers=False)
        if i<5:
            ax.set_title(titles[i])
            data,lons=add_cyclic_point(boreal_pfts.isel(natpft=i).values,coord=boreal_pfts['lon'])
            cs=ax.contourf(lons,boreal_pfts['lat'],data, transform = ccrs.PlateCarree(),
                                cmap ='Greens', extend='both', levels = np.linspace(0,100, 11) )
        ax.title.set_size(15)
        ax.title.set_position([0.5,1.5])

    plt.tight_layout()
    # Add colorbar in the remaining axis
    plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.9, wspace=0.1, hspace=0.1)
    cbar_ax = p.fig.add_axes([0.5, 0.25, 0.4, 0.03]) #[left, bottom, width, height]
    cbar=p.fig.colorbar(cs,cax=cbar_ax ,orientation='horizontal')
    cbar.ax.set_title(boreal_pfts.long_name, size = 14 )

    plt.suptitle("Boreal PFTs", size=20, y = 0.95, fontweight = 'bold')
    plt.show()


################ Projections

def ax_map_properties(ax, alpha=0.3, coastlines=True, gridlines=True, earth = False, ocean=True, land=True, borders=True, rivers=True, provinces=False):
    """Set default map properties on the axis"""
    if coastlines: ax.coastlines()
    if gridlines: ax.gridlines()
    if ocean: ax.add_feature(cartopy.feature.OCEAN, zorder=0, alpha=alpha)
    if land: ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor='black', alpha=alpha)
    if borders: ax.add_feature(cfeature.BORDERS, alpha=0.3)
    if rivers: ax.add_feature(cfeature.RIVERS)
    if earth: ax.stock_img()

def cut_extent_Orthographic(ax, lat=None, extent=None):
    """Return circle where to cut the circular plot, given the latitude"""
    if extent:
        ax.set_extent(extent, crs = ccrs.PlateCarree())
    elif lat:
        ax.set_extent([-180,180, lat,90], crs = ccrs.PlateCarree())
    else:
        ax.set_extent([-180,180,-90,90], crs = ccrs.PlateCarree())
    # Compute a circle in axes coordinates, which we can use as a boundary for the map.
    # We can pan/zoom as much as we like - the boundary will be permanently circular.
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)
    ax.set_boundary(circle, transform=ax.transAxes)
    
################ Dominant vegetation plot

def dominant_vegetation(veg_ds):
    """
    Create DataArray with .values() as the corresponding dominant PFTs number
    """
    
    pfts_list = list(veg_ds.natpft.values)
    # Start copying the first PFT, fill the array of respective PFT number and filter by lnd_frac
    dominant_veg = veg_ds.isel(natpft=0).copy()
    dominant_veg[:] = pfts_list[0]
    dominant_veg = dominant_veg.where(veg_ds.sel(natpft=pfts_list[0])>0.).drop('natpft')
    #dominant_veg.plot(); plt.show()

    # Building the dominant veg rappresentation:
    # find max PFT value in each grid cell and compare to each "layer" of PFT
    # -> if equal to the max, then substitute the PFT number with the new max PFT number
    pfts_max = veg_ds.max(dim='natpft')
    pfts_max=pfts_max.where(pfts_max>0.)
    #pfts_max.plot(); plt.show()

    for p in range(len(pfts_list)):
        pft_filter=veg_ds.sel(natpft=pfts_list[p]) == pfts_max
        # pft_filter is a True-False array (where -lat/lon- is equal to max values)
        pft_filter=pft_filter
        dominant_veg = xr.where(pft_filter, pfts_list[p], dominant_veg)
        # where True, PFT number. Otherwise keep dominant veg value

        dominant_veg = dominant_veg.drop('natpft').rename('PFTs')
    return dominant_veg

def discrete_mapping_elements(col_dict, labels):
    """Return colormap, normalizer, format and ticks for colorbar in order to plot a discrete map
        Args:
            - col_dict (dictionary): dictionary with values as .keys() and respective color as .items()
            - labels (list of strings): names relative to values"""
    # Create a colormap
    cm = ListedColormap([col_dict[x] for x in col_dict.keys()])
    # Normalizer:
    ## Prepare bins for the normalizer
    norm_bins = np.sort([*col_dict.keys()]) + 0.5
    norm_bins = np.insert(norm_bins, 0, np.min(norm_bins) - 1.0)
    ## Make normalizer and formatter
    norm = matplotlib.colors.BoundaryNorm(norm_bins, len(labels), clip=True)
    fmt = matplotlib.ticker.FuncFormatter(lambda x, pos: labels[norm(x)])
    # Create ticks to have equidistance between ticks
    diff = norm_bins[1:] - norm_bins[:-1]
    tickz = norm_bins[:-1] + diff / 2
    return cm, norm, fmt, tickz

def plot_dominant_vegetation(da_pfts, title, col_dict, labels, projection = ccrs.PlateCarree(), extent=None, figsize=[12,8], alpha=0.8):
    """ Plot dominant vegetation on the base on dominant PFT percentage.
        Args:
            - da_pfts (DataArray): PFTs DataArray with dim (lon, lat, natpft)
            - title (string): title of the plot
            - col_dict (dict): keys are PFTs number (int) and values are color names (string)
            - labels (list of string): legend label - PFT names
            - projection (ccrs object): projection of the map. Default: ccrs.PlateCarree()
            - extent (list of float): list of coordinate to zoom on [lon_min, lon_max, lat_min, lat_max]. Default None.
            - alpha (float): opacity of land-ocean background
    """
    
    dominant_boreal = dominant_vegetation(da_pfts)
    #dominant_boreal.plot(); plt.show()

    ############# Preparation for plotting:
    cm, norm, fmt, tickz = discrete_mapping_elements(col_dict, labels)

    ############# Plotting:
    
    fig = plt.figure(1, figsize=figsize)#, dpi=300)
    ax = plt.axes(projection=projection)
    
    if extent:
        if projection == ccrs.PlateCarree():
            ax.set_extent(extent, crs = ccrs.PlateCarree())
        else:
            cut_extent_Orthographic(ax, extent=extent)

    p= dominant_boreal.plot.pcolormesh(ax=ax, x='lon', y='lat', cmap=cm, norm=norm, transform=ccrs.PlateCarree(),
                                    add_colorbar=False)
    cb = fig.colorbar(p, ax=[ax], format=fmt, ticks=tickz, location = 'top', shrink=1/15*len(da_pfts.natpft.values), aspect=len(da_pfts.natpft.values)*3)

    ax_map_properties(ax, alpha=alpha)
    ax.gridlines(draw_labels=True)

    if projection == ccrs.PlateCarree():
        plt.title(title, y=1.25, size='xx-large', weight='bold')
    else:
        plt.title(title, y=1.15, size='xx-large', weight='bold')
        plt.tight_layout()
    plt.show()
