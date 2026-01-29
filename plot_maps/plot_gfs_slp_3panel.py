import time, os, sys
import numpy as np
from datetime import datetime, timedelta
import grib2io
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
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

exit

# 1. Open the local GRIB2 file
filename_gfsv17 = '/lfs/h2/emc/gfstemp/emc.global/comroot/retrov17_01_realtime/gfs.20260129/00/products/atmos/grib2/0p25/gfs.t00z.pres_a.0p25.f078.grib2'
with grib2io.open(filename_gfsv17) as f_v17:

    # 2. Select the specific messages we want
    # GFS Shortnames: TMP (Temp), PRMSL (Pressure), RH (Rel. Humidity)
    print("Loaded file!")
    tmp_msg = f_v17.select(shortName='TMP', level='surface')[0]
    mslp_msg = f_v17.select(shortName='PRMSL', level='mean sea level')[0]
    rh_msg = f_v17.select(shortName='RH', level='850 mb')[0]
    print("Select parameters from file!")

    # 3. Extract data and coordinates
    # grib2io provides lats/lons directly from the message
    lats, lons = tmp_msg.latlons()
    print("Extracted lat/lons!")

    # Extract values
    tmp_data = tmp_msg.data
    mslp_data = mslp_msg.data / 100.0  # Convert Pa to hPa/mb
    rh_data = rh_msg.data
    print("Extracted parameters from file!")

# 4. Create the 3-Panel Plot
# 1. Create the figure
fig = plt.figure(figsize=(16, 12))

# 2. Define a 2x2 grid
gs = gridspec.GridSpec(2, 2, figure=fig)

plot_configs = [
    {'data': tmp_data,  'cmap': 'magma', 'title': 'Surface Temp (K)'},
    {'data': mslp_data, 'cmap': 'gist_rainbow', 'title': 'MSLP (hPa)'},
    {'data': rh_data,   'cmap': 'GnBu',  'title': '850mb Rel. Humidity (%)'}
]

# Define the grid locations: [row, col] or [row, span]
# gs[0, 0] = Top Left, gs[0, 1] = Top Right, gs[1, :] = Bottom Center
grid_locs = [gs[0, 0], gs[0, 1], gs[1, :]]

for i, loc in enumerate(grid_locs):
    config = plot_configs[i]
    
    # Add subplot with projection
    ax = fig.add_subplot(loc, projection=ccrs.PlateCarree())

    # Geographic features
    ax.add_feature(cfeature.COASTLINE, linewidth=1)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, edgecolor='gray', alpha=0.5)

    # Define zoom
    ax.set_extent([-125, -70, 22, 52], crs=ccrs.PlateCarree())

    # Plot data
    im = ax.contourf(lons, lats, config['data'], 20,
                     transform=ccrs.PlateCarree(), cmap=config['cmap'])

    # Colorbar and Titles
    plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.08, fraction=0.046)
    ax.set_title(config['title'], fontweight='bold', fontsize=14)

# Adjust layout to prevent overlapping
plt.suptitle(f"Mean Sea Level Pressure | Initialized: {init_dt.strftime('%Y-%m-%d %HZ')} (Fhr: {fhr}) | Valid: {valid_dt.strftime('%Y-%m-%d %HZ')}", fontsize=20)
plt.tight_layout()
plt.savefig('test_plot.png')
