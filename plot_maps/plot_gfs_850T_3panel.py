import time, os, sys
import numpy as np
from datetime import datetime, timedelta
import grib2io
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.feature as cfeature
import io
from PIL import Image
import matplotlib.image as image
from matplotlib.gridspec import GridSpec
from scipy import ndimage
from scipy.ndimage import gaussian_filter
from netCDF4 import Dataset
import pyproj
import cartopy
import cartopy.io.shapereader as shpreader

#####################################################

pdy = str(sys.argv[1])             #20251120
cyc = str(sys.argv[2])		   #12 
#fhr = str(sys.argv[3])             #24 
grid = str(sys.argv[3])            #conus
show_colorbar="yes"

print("pdy:", pdy)
print("cyc:", cyc)
#print("fhr:", fhr)
print("grid:", grid)

init_str = str(pdy)
init_hour = int(cyc)

#Create the datetime object
# strptime converts the string to a datetime object
init_dt = datetime.strptime(init_str, "%Y%m%d").replace(hour=init_hour)

####################################################

img_counter=0
print("img_counter:", img_counter)

####################################################

for fhr in range(0, 193, 6):
#for fhr in range(0, 385, 6):
    # Use f-string to format with leading zeros (e.g., 000, 006)
    fhr_str = f"{fhr:03d}"
    fcst_hour= int(fhr)
    
    # Add the forecast lead time
    forecast_delta = timedelta(hours=fcst_hour)
    valid_dt = init_dt + forecast_delta

    # Print the results in a readable format
    print(f"Initialization Time: {init_dt.strftime('%Y-%m-%d %HZ')}")
    print(f"Forecast Lead:       {fcst_hour} hours")
    print(f"Valid Time:          {valid_dt.strftime('%Y-%m-%d %HZ')}")

    # Open GFSv16 GRIB2 file and extract parameters
    filename_gfsv16 = f"/lfs/h1/ops/prod/com/gfs/v16.3/gfs.{pdy}/{cyc}/atmos/gfs.t{cyc}z.pgrb2.0p25.f{fhr_str}"
    with grib2io.open(filename_gfsv16) as f_v16:

        # Select the specific messages we want
        t850_msg_v16 = f_v16.select(shortName='TMP', level='850 mb')[0]

        # Extract values
        t850_data_v16 = t850_msg_v16.data - 273.15  # Convert K to C

    # Open GFSv17 GRIB2 file and extract parameters
    #filename_gfsv17 = f"/lfs/h2/emc/vpppg/noscrub/alicia.bentley/GFSv17archive/data/gfs.{pdy}/{cyc}/products/atmos/grib2/0p25/gfs.t{cyc}z.pres_a.0p25.f{fhr_str}.grib2"
    #filename_gfsv17 = f"/lfs/h2/emc/gfstemp/emc.global/EVS_archive/retrov17_01/gfs.{pdy}/{cyc}/products/atmos/grib2/0p25/gfs.t{cyc}z.pres_a.0p25.f{fhr_str}.grib2"
    filename_gfsv17 = f"/lfs/h2/emc/gfstemp/emc.global/comroot/retrov17_01_realtime/gfs.{pdy}/{cyc}/products/atmos/grib2/0p25/gfs.t{cyc}z.pres_a.0p25.f{fhr_str}.grib2"
    with grib2io.open(filename_gfsv17) as f_v17:

        # Select the specific messages we want
        t850_msg_v17 = f_v17.select(shortName='TMP', level='850 mb')[0]

        # Extract values
        t850_data_v17 = t850_msg_v17.data - 273.15  # Convert K to C

        # Calculate the difference (e.g., Panel 1 minus Panel 2)
        diff_data = t850_data_v17 - t850_data_v16

        # Extract data and coordinates
        lats, lons = t850_msg_v17.latlons()

#########################################################

    # Create the 3-Panel Plot
    fig = plt.figure(figsize=(16, 12))

    # Define a 2x2 grid
    gs = gridspec.GridSpec(2, 2, figure=fig)

    # Define the specific normalization (Panels 1 & 2)
    t850_norm = mcolors.Normalize(vmin=-44, vmax=36)
    t850_levels = np.arange(-44, 40, 4)

    # New normalization for the difference plot so that near 0 is white
    diff_norm = mcolors.TwoSlopeNorm(vcenter=0, vmin=-40, vmax=40)
    diff_levels = np.arange(-40, 41, 2)

    # Take 42 colors from the 'seismic' colormap
    base_cmap = plt.get_cmap('seismic', 42)
    new_colors = base_cmap(np.linspace(0, 1, 42))

    # Force the middle two colors (index 21 and 22) to be white
    # Format is [Red, Green, Blue, Alpha]
    new_colors[20] = [1, 1, 1, 1]  # Middle-left
    new_colors[21] = [1, 1, 1, 1]  # Middle-right

    # Create the new colormap
    white_center_cmap = mcolors.ListedColormap(new_colors)
    print('Created new colormap!')

    # Update configs with specific 'norm' and 'levels'
    plot_configs = [
        {'data': t850_data_v16, 'cmap': 'nipy_spectral', 'norm': t850_norm, 'levels': t850_levels, 'title': 'GFSv16 850T (Celcius)'},
        {'data': t850_data_v17, 'cmap': 'nipy_spectral', 'norm': t850_norm, 'levels': t850_levels, 'title': 'GFSv17 850T (Celcius)'},
        {'data': diff_data,     'cmap': 'seismic',      'norm': diff_norm, 'levels': diff_levels, 'title': 'GFSv17 minus GFSv16 850T (Celcius)'}
    ]

    # Define the grid locations: [row, col] or [row, span]
    # gs[0, 0] = Top Left, gs[0, 1] = Top Right, gs[1, :] = Bottom Center
    grid_locs = [gs[0, 0], gs[0, 1], gs[1, :]]

#########################################################

    for i, loc in enumerate(grid_locs):
        config = plot_configs[i]

        # Grab your raw data from the config or GRIB2 message
        raw_data = config['data']

        # Apply the filter
        # sigma=1.0 is a good starting point for 0.25-degree GFS.
        # A higher sigma means MORE smoothing. 2.0 may be too much.
        smoothed_data = gaussian_filter(raw_data, sigma=0.5)
 
        # Add subplot with projection
        ax = fig.add_subplot(loc, projection=ccrs.PlateCarree())

        # Geographic features
        ax.add_feature(cfeature.COASTLINE, linewidth=1)
        ax.add_feature(cfeature.BORDERS, linewidth=1)
        ax.add_feature(cfeature.STATES, edgecolor='gray', linewidth=1.5, alpha=0.5)

        # Define domain
        ax.set_extent([-130, -65, 20, 56], crs=ccrs.PlateCarree())

        # Check if we are on the third panel and apply special cmap
        if i == 2:
            current_cmap = white_center_cmap
        else:
            current_cmap = config['cmap']

        # Plot the shading
        # Subsample the data (skip points). Skipping every 2nd or 3rd point 
        # makes it much faster with almost zero visual loss on a 0.25 grid.
        skip = 2
        im = ax.contourf(lons[::skip, ::skip], 
                     lats[::skip, ::skip], 
                     smoothed_data[::skip, ::skip],
                     levels=config['levels'],
                     norm=config['norm'],
                     cmap=current_cmap,
                     transform=ccrs.PlateCarree(),
                     extend='both',
                     antialiased=True) # Bonus speed boost when False, but looks nasty
        print('Got through shading!')

        # Plot the contour lines
        # Only add lines if it's one of the MSLP panels (0 or 1)
        #skip = 4
        if i < 2:
             contours = ax.contour(lons[::skip, ::skip],
                     lats[::skip, ::skip],
                     smoothed_data[::skip, ::skip],
                     levels=config['levels'], 
                     colors='black', 
                     linewidths=0.5, 
                     transform=ccrs.PlateCarree(),
                     antialiased=True)  # Bonus speed boost when False, but looks nasty

             # Add labels to the lines (e.g., '1012')
             # Reduce padding (default is 4) to allow more labels to fit in tight spaces
             ax.clabel(contours, inline=True, fontsize=8, fmt='%i', inline_spacing=1)
             print('Added contour lines!')

        # Colorbar and Titles
        plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.06, fraction=0.055)
        ax.set_title(config['title'], fontweight='bold', fontsize=14)

#################################################

    # Add a title and adjust layout to prevent overlapping
    plt.suptitle(f"850-hPa Temperature (850T) | Initialized: {init_dt.strftime('%Y-%m-%d %HZ')} (Fhr: {fhr_str}) | Valid: {valid_dt.strftime('%Y-%m-%d %HZ')}", fontsize=20)
    plt.tight_layout()
    plt.savefig(f"image_{img_counter}.png")

    img_counter = img_counter + 1
    print("img_counter:", img_counter)
