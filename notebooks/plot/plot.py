###### This python file collects fuctions to modify PFT configuration, such as in surfdata_map file

####### Import packages
import numpy as np
import pandas as pd
import xarray as xr

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors

import cartopy
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import warnings; warnings.filterwarnings('ignore')
import matplotlib.path as mpath
from textwrap import wrap

plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'
plt.rcParams['font.size'] = '15'
#plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['figure.titlesize'] = '22'
plt.rcParams['axes.titlesize'] = '18'

################ Miscellaneous ################
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def dict_to_legend(dct):
    """Support function for legend display.
      Convert a dict in the format {item1: amount1, item2:amount2...}
      into a list of strings in the format ['item1 - amount1', 'item2 - amount2', ...]
    """
    return ["{} – {}".format(item, amount) for item, amount in dct.items()]
    
def plot_title(title):
    """Plot the give title. Useful if plotting multiple figures, gathered under a same main title."""
    fig, ax = plt.subplots(1,1, figsize=(10, 0.5))
    ax.axis('off')
    plt.suptitle(title, weight='bold', size='xx-large', y=0.5)
    plt.show()
    
class MidpointNormalize(colors.Normalize):
#https://matplotlib.org/3.2.2/gallery/userdemo/colormap_normalizations_custom.html
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

################ Projections ################
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def ax_map_properties(ax, alpha=0.3, coastlines=True, gridlines=True, earth = False, ocean=True, land=True, borders=True, rivers=True, provinces=False):
    """Set default map properties on the axis"""
    if coastlines: ax.coastlines()
    if gridlines: ax.gridlines(alpha=0.3)
    if ocean: ax.add_feature(cartopy.feature.OCEAN, zorder=0, alpha=alpha)
    if land: ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor='black', alpha=alpha)
    if borders: ax.add_feature(cfeature.BORDERS, alpha=0.3)
    if rivers: ax.add_feature(cfeature.RIVERS)
    if earth: ax.stock_img()

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def cut_extent_Orthographic(ax, lat=None, extent=None):
    """Return circle where to cut the circular plot, given the latitude"""
    if extent:
        ax.set_extent(extent, crs = ccrs.PlateCarree())
    elif lat:
        ax.set_extent([-180,180, lat,90], crs = ccrs.PlateCarree())
    else:
        ax.set_extent([-180,180,-90,90], crs = ccrs.PlateCarree())
    # Compute a circle in axes coordinates, which we can use as a boundary for the map.
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)
    ax.set_boundary(circle, transform=ax.transAxes)
        
######### Maps ###############
fig_folder = '../../figures/results/'
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def boreal_map(da, title, figsize = [10,8], ax=None, projection=ccrs.Orthographic(0, 90), extent_lat = None,
                   grid=True, earth=False, contourf=False, units=None, cbar_kwargs={}, **kwargs):
    """Plot a spatial distribution of 'da', specially adapted for boreal and artic area.
    Args:
        - da (xr.DataArray): variable to plot with dimension [lat,lon]
        - ax (matplotlib.axes.Axes): axis to plot on. Optional. If None, a figure is created.
        - figsize (tuple): figure size (if ax=None)
        - projection (ccrs.): geographical projection
        - extent_lat (float): latitude over which the distribution will be depicted
        - grid (bool): display grid lines
        - earth (bool): display earth background
        - contourf (bool): contourf plot type. Default: pcolormesh
        - units (string): units for the colorbar label
        - cbar_kwargs (dict): colorbar arguments
        - kwargs (dict): arguments to pass to the xr.da.plot()
    """
    
    
    # Add axis if it not given - useful to plot multiple subplots in one figure
    if not ax:
        fig = plt.figure(1, figsize=figsize)#,dpi=100)
        ax = plt.axes(projection=projection)

    # Zoom on the map according to boreal_lat
    # Opposite of ax.set_global()
    if extent_lat: cut_extent_Orthographic(ax, extent_lat)

    # Gather all the arguments of the plot
    plot_args = dict(ax=ax, x='lon', y='lat', transform=ccrs.PlateCarree(), add_colorbar=False, **kwargs)
    
    # If not plot.contourf -> plot.pcolormesh
    if not contourf: p = da.plot(**plot_args) #pcolormesh
    else: p = da.plot.contourf(**plot_args)
        
    # Add common colorbar
    for arg in ['location', 'pad', 'shrink', 'aspect', 'extend']:
        if not arg in list(cbar_kwargs.keys()):
            if arg == 'location': cbar_kwargs[arg] = 'bottom'
            if arg == 'pad': cbar_kwargs[arg] =  0.05
            if arg == 'shrink': cbar_kwargs[arg] = 0.8
            if arg == 'aspect': cbar_kwargs[arg] = 35
            if arg == 'extend': cbar_kwargs[arg] = 'both'
            #if arg == 'label': cbar_kwargs[arg] = da.long_name+'\n['+da.units+']'
    cbar = plt.colorbar(p, ax = [ax], **cbar_kwargs)
    if not units: units = da.units
    cbar.set_label("\n".join(wrap(da.long_name+'\n['+units+']', 35)))
    #cbar = plt.colorbar(p, ax = [ax], location = 'bottom', pad=0.05,shrink=0.8, aspect=40, extend='both', **cbar_kwargs, label=da.long_name+'\n['+da.units+']')#'PTF on the natveg landunit [% of landunit]')

    # Costum axis features
    ax_map_properties(ax, gridlines=grid, earth=earth, rivers=False)
    if projection==ccrs.PlateCarree(): ax.set_aspect('auto')
    ax.set_title(title)#, weight='bold') #size='x-large'
    if not ax: plt.show()
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def set_colorbar(ds, kwargs):
    if 'vmax' in list(kwargs.keys()):
        vmax = kwargs['vmax']
        kwargs['vmin'] = - vmax
    if 'cbar_kwargs' in list(kwargs.keys()):
        kwargs['cbar_kwargs']['ticks'] = [-vmax, -vmax*0.5, 0, vmax*0.5, vmax]
    if not 'norm' in list(): kwargs['norm'] = MidpointNormalize(midpoint=0.)
    #if 'levels' in list(kwargs.keys()):
        #ds = ds.where(ds!=0.)
        
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def plot_difference_map(da_dict, case1, case2, variable, ax = None, relative=False, cmap='RdBu_r', boreal_lat=45., **kwargs):
    
    da1 = da_dict[case1][variable].mean('time')
    da2 = da_dict[case2][variable].mean('time')
    if variable=='ACTNL' or variable=='ACTREL':
        da1 = da_dict[case1][variable].mean('time')/da_dict[case1]['FCTL'].mean('time')
        da2 = da_dict[case2][variable].mean('time')/da_dict[case2]['FCTL'].mean('time')
    diff = (da1-da2)
    if relative:
        diff = diff/da2*100
        if not 'vmax' in list(kwargs.keys()): kwargs = dict(vmax=100, **kwargs)
    if variable =='N_AER': diff=diff.isel(lev=-1)
        
    set_colorbar(diff, kwargs)

    boreal_map(diff, ax = ax, title=case1+' – '+case2, cmap=cmap, extent_lat = boreal_lat, units = '%' if relative else None, **kwargs)
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def spatial_averages(ds_dict, variable, title, relative = False, **kwargs):
    
    fig, axes = plt.subplots(3,2, figsize=[12,16], subplot_kw={'projection':ccrs.Orthographic(0, 90)})

    #plot_args = dict(cbar_kwargs={'extend':'both'}, **kwargs)

    plot_difference_map(ds_dict, 'IDEAL-ON', 'CTRL', variable, ax=axes.flat[0], relative=relative, **kwargs)
    plot_difference_map(ds_dict, 'REAL-ON', 'CTRL', variable, ax=axes.flat[1], relative=relative, **kwargs)
    plot_difference_map(ds_dict, 'IDEAL-ON', 'IDEAL-OFF', variable, ax=axes.flat[2], relative=relative, **kwargs)
    plot_difference_map(ds_dict, 'REAL-ON', 'REAL-OFF', variable, ax=axes.flat[3], relative=relative, **kwargs)
    plot_difference_map(ds_dict, 'IDEAL-OFF', 'CTRL', variable, ax=axes.flat[4], relative=relative, **kwargs)
    plot_difference_map(ds_dict, 'REAL-OFF', 'CTRL', variable, ax=axes.flat[5], relative=relative, **kwargs)
    plt.suptitle(title)
    figtitle = fig_folder+variable
    if relative: figtitle=figtitle+'_relative'
    plt.savefig(figtitle+'.pdf')
    plt.show()

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def plot_difference_map_winter_summer(axes, da_dict, case1, case2, variable, seasons = ['DJF', 'JJA'], boreal_lat=45., relative = False, **kwargs):
    
    da1 = da_dict[case1][variable].groupby('time.season').mean('time')
    da2 = da_dict[case2][variable].groupby('time.season').mean('time')
    
    if variable=='ACTNL' or variable=='ACTREL':
        da1 = da_dict[case1][variable].groupby('time.season').mean('time')/da_dict[case1]['FCTL'].groupby('time.season').mean('time')
        da2 = da_dict[case2][variable].groupby('time.season').mean('time')/da_dict[case2]['FCTL'].groupby('time.season').mean('time')
    diff = (da1-da2)
    if relative:
        diff = diff/da2*100
        if not 'vmax' in list(kwargs.keys()): kwargs = dict(vmax=100, **kwargs)
    
    if variable=='N_AER': diff=diff.isel(lev=-1)
        
    set_colorbar(diff, kwargs)

    for i, season in enumerate(seasons):
        boreal_map(diff.sel(season=season), ax=axes.flat[i],title=season, cmap='RdBu_r', extent_lat = boreal_lat, units = '%' if relative else None, **kwargs)
    plt.subplots_adjust(bottom=0.3, top=0.8)
    plt.suptitle(case1+' – '+case2, y=0.9,size=18)
    plt.tight_layout()
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def spatial_averages_winter_summer(ds_dict, variable, title, figsize=[20,30], dpi=300, relative = False, cbar_kwargs = {},**kwargs):
    backend = mpl.get_backend()
    mpl.use('agg')

    plot_args = dict(nrows=1, ncols=2, figsize=[figsize[0]/4.*1.3, figsize[1]/6.], dpi=dpi, subplot_kw={'projection':ccrs.Orthographic(0, 90)})
    
    figs = []
    axes = []
    for i, cases in enumerate([['IDEAL-ON', 'CTRL'], ['REAL-ON', 'CTRL'], ['IDEAL-ON', 'IDEAL-OFF'], ['REAL-ON', 'REAL-OFF'], ['IDEAL-OFF', 'CTRL'], ['REAL-OFF', 'CTRL']]):
        fig, ax = plt.subplots(**plot_args)
        axes.append(ax)
        plot_difference_map_winter_summer(axes[i], ds_dict, *cases, variable, relative = relative, cbar_kwargs=dict(shrink=1.1, aspect=25, **cbar_kwargs), **kwargs)
        figs.append(fig)
    
    a_list = []
    for fig in figs:
        c = fig.canvas
        c.draw()
        a_list.append(np.array(c.buffer_rgba()))
        
    a_top = np.hstack(a_list[:2])
    a_middle = np.hstack(a_list[2:4])
    a_bottom = np.hstack(a_list[4:])
    a = np.vstack((a_top, a_middle, a_bottom))
        
    mpl.use(backend)
    fig,ax = plt.subplots(figsize=figsize)
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_axis_off()
    ax.matshow(a)
    plt.suptitle(title, size=33, y=0.9)
    figtitle = fig_folder+variable+'_seasons'
    if relative: figtitle=figtitle+'_relative'
    plt.savefig(figtitle+'.pdf')
    plt.show()







#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def plot_difference_map_4seasons(da_dict, case1, case2, variable, title, relative=True, **kwargs):
    seasons = ['DJF', 'MAM','JJA', 'SON']
    
    da1 = da_dict[case1][variable].groupby('time.season').mean('time')
    da2 = da_dict[case2][variable].groupby('time.season').mean('time')
    
    if variable=='ACTNL' or variable=='ACTREL':
        da1 = da_dict[case1][variable].groupby('time.season').mean('time')/da_dict[case1]['FCTL'].groupby('time.season').mean('time')
        da2 = da_dict[case2][variable].groupby('time.season').mean('time')/da_dict[case2]['FCTL'].groupby('time.season').mean('time')
        #ds_[var] = ds_[var].where((ds_['FCTL'] != 0))
    diff = (da1-da2)
    if relative:
        diff = diff/da2*100
        if 'vmax' in list(kwargs.keys()): kwargs['vmax']=100
        else: kwargs = dict(vmax=100, **kwargs)
        if 'vmin' in list(kwargs.keys()): kwargs['vmin']=-100
        else: kwargs = dict(vmin=-100, **kwargs)
    if variable=='N_AER': diff=diff.isel(lev=-1)
        
    fig, axes = plt.subplots(1,4, figsize=[17,5], subplot_kw={'projection':ccrs.Orthographic(0, 90)})#,dpi=100)
    
    for i, season in enumerate(seasons):
        boreal_map(diff.sel(season=season), ax=axes.flat[i], title=season, cmap='RdBu_r', extent_lat =45.,**kwargs)
    plt.suptitle(title+':\n'+case1+' – '+case2, y=1.05)
    plt.show()
