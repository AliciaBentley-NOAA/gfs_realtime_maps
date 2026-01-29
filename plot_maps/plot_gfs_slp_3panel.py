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
from netCDF4 import Dataset
import pyproj
import cartopy
import cartopy.io.shapereader as shpreader

pdy = str(sys.argv[1])             #20251120
cyc = str(sys.argv[2])		   #12 
fhr = str(sys.argv[3])             #24 
grid = str(sys.argv[4])            #conus
fcst_file = str(sys.argv[5])        #[path to GFS forecast file]
case = str(sys.argv[6])            #realtime
show_colorbar="yes"

print("pdy:", pdy)
print("cyc:", cyc)
print("fhr:", fhr)
print("grid:", grid)
print("fcst_file:", fcst_file)
print("case:", case)

init_str = str(pdy)
init_hour = int(cyc)
fcst_hour= int(fhr)

#Create the datetime object
# strptime converts the string to a datetime object
init_dt = datetime.strptime(init_str, "%Y%m%d").replace(hour=init_hour)

# Add the forecast lead time
forecast_delta = timedelta(hours=fcst_hour)
valid_dt = init_dt + forecast_delta

# Print the results in a readable format
print(f"Initialization Time: {init_dt.strftime('%Y-%m-%d %HZ')}")
print(f"Forecast Lead:       {fcst_hour} hours")
print(f"Valid Time:          {valid_dt.strftime('%Y-%m-%d %HZ')}")

# 1. Open the local GRIB2 file
filename_gfsv16 = '/lfs/h1/ops/prod/com/gfs/v16.3/gfs.20260129/00/atmos/gfs.t00z.pgrb2.0p25.f078'
with grib2io.open(filename_gfsv16) as f_v16:

    # Select the specific messages we want
    mslp_msg_v16 = f_v16.select(shortName='PRMSL', level='mean sea level')[0]

    # Extract values
    mslp_data_v16 = mslp_msg_v16.data / 100.0  # Convert Pa to hPa/mb

filename_gfsv17 = '/lfs/h2/emc/gfstemp/emc.global/comroot/retrov17_01_realtime/gfs.20260129/00/products/atmos/grib2/0p25/gfs.t00z.pres_a.0p25.f078.grib2'
with grib2io.open(filename_gfsv17) as f_v17:

    # Select the specific messages we want
    mslp_msg_v17 = f_v17.select(shortName='PRMSL', level='mean sea level')[0]

    # Extract values
    mslp_data_v17 = mslp_msg_v17.data / 100.0  # Convert Pa to hPa/mb

    # Calculate the difference (e.g., Panel 1 minus Panel 2)
    diff_data = mslp_data_v17 - mslp_data_v16

    # Extract data and coordinates
    lats, lons = mslp_msg_v17.latlons()

# 2. Create the 3-Panel Plot
fig = plt.figure(figsize=(16, 12))

# 3. Define a 2x2 grid
gs = gridspec.GridSpec(2, 2, figure=fig)

# Define the specific normalization for MSLP (Panels 1 & 2)
mslp_norm = mcolors.Normalize(vmin=968, vmax=1052)
mslp_levels = np.arange(968, 1056, 4)

# New normalization for the difference plot to ensure 0 is white
diff_norm = mcolors.TwoSlopeNorm(vcenter=0, vmin=-20, vmax=20)
diff_levels = np.arange(-20, 21, 1)

# Update configs with specific 'norm' and 'levels'
plot_configs = [
    {'data': mslp_data_v16, 'cmap': 'gist_rainbow', 'norm': mslp_norm, 'levels': mslp_levels, 'title': 'GFSv16 MSLP (hPa)'},
    {'data': mslp_data_v17, 'cmap': 'gist_rainbow', 'norm': mslp_norm, 'levels': mslp_levels, 'title': 'GFSv17 MSLP (hPa)'},
    {'data': diff_data,     'cmap': 'seismic',      'norm': diff_norm, 'levels': diff_levels, 'title': 'GFSv17 MSLP minus GFSv16 MSLP (hPa)'}
]

# 4. Define the grid locations: [row, col] or [row, span]
# gs[0, 0] = Top Left, gs[0, 1] = Top Right, gs[1, :] = Bottom Center
grid_locs = [gs[0, 0], gs[0, 1], gs[1, :]]

for i, loc in enumerate(grid_locs):
    config = plot_configs[i]
    
    # Add subplot with projection
    ax = fig.add_subplot(loc, projection=ccrs.PlateCarree())

    # Geographic features
    ax.add_feature(cfeature.COASTLINE, linewidth=1)
    ax.add_feature(cfeature.BORDERS, linewidth=1)
    ax.add_feature(cfeature.STATES, edgecolor='gray', linewidth=1.5, alpha=0.5)

    # Define zoom
    ax.set_extent([-130, -65, 20, 56], crs=ccrs.PlateCarree())

    # Plot data
    # Add the shaded color fill
    im = ax.contourf(lons, lats, config['data'], 
                     levels=config['levels'],
                     norm=config['norm'], 
                     cmap=config['cmap'],
                     transform=ccrs.PlateCarree(),
                     extend='both')

    # Add the contour lines
    # We only add lines if it's one of the MSLP panels (0 or 1)
    if i < 2:
        contours = ax.contour(lons, lats, config['data'], 
                              levels=config['levels'], 
                              colors='black', 
                              linewidths=0.5, 
                              transform=ccrs.PlateCarree())
        
        # Add labels to the lines (e.g., '1012')
        ax.clabel(contours, inline=True, fontsize=8, fmt='%i')

    # Inside your loop, for the 3rd panel (index 2)
    #if i == 2:
        # Add a thicker black line at the 0 value
        #ax.contour(lons, lats, config['data'], levels=[0], colors='black', linewidths=1.5, transform=ccrs.PlateCarree())

    # Colorbar and Titles
    plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.06, fraction=0.055)
    ax.set_title(config['title'], fontweight='bold', fontsize=14)

# 5 Adjust layout to prevent overlapping
plt.suptitle(f"Mean Sea Level Pressure (MSLP) | Initialized: {init_dt.strftime('%Y-%m-%d %HZ')} (Fhr: {fhr}) | Valid: {valid_dt.strftime('%Y-%m-%d %HZ')}", fontsize=20)
plt.tight_layout()
plt.savefig('test_plot.png')
