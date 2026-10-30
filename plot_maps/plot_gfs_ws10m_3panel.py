import time, os, sys
import numpy as np
from datetime import datetime, timedelta
import grib2io
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap, Normalize
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

#####################################################

pdy = str(sys.argv[1])             #20251120
cyc = str(sys.argv[2])		   #12 
#fhr = str(sys.argv[3])             #24 
grid = str(sys.argv[3])            #conus
DATA_PATH = str(sys.argv[4])       # /lfs/h2/emc/vpppg/noscrub/alicia.bentley/feb2026
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
        u10m_msg_v16 = f_v16.select(shortName='UGRD', level='10 m above ground')[0]
        v10m_msg_v16 = f_v16.select(shortName='VGRD', level='10 m above ground')[0]

        # Extract values
        u10m_data_v16 = u10m_msg_v16.data
        v10m_data_v16 = v10m_msg_v16.data

        # Calculate 10m wind speed using the Pythagorean formula
        ws10m_data_v16 = np.sqrt(u10m_data_v16**2 + v10m_data_v16**2)

    # Open GFSv17 GRIB2 file and extract parameters
    filename_gfsv17 = f"{DATA_PATH}/gfs.{pdy}/{cyc}/products/atmos/grib2/0p25/gfs.t{cyc}z.pres_a.0p25.f{fhr_str}.grib2"
    with grib2io.open(filename_gfsv17) as f_v17:

        # Select the specific messages we want
        u10m_msg_v17 = f_v17.select(shortName='UGRD', level='10 m above ground')[0]
        v10m_msg_v17 = f_v17.select(shortName='VGRD', level='10 m above ground')[0]
        
        # Extract values
        u10m_data_v17 = u10m_msg_v17.data 
        v10m_data_v17 = v10m_msg_v17.data 

        # Calculate 10m wind speed using the Pythagorean formula
        ws10m_data_v17 = np.sqrt(u10m_data_v17**2 + v10m_data_v17**2)

        # Calculate the difference (e.g., Panel 1 minus Panel 2)
        diff_data = ws10m_data_v17 - ws10m_data_v16

        # Extract data and coordinates
        lats, lons = u10m_msg_v17.latlons()

    # Shift longitudes from [0, 360] to [-180, 180]
    lons = np.where(lons > 180, lons - 360, lons)

    # If lons is a 2D meshgrid, we only want the 1D vector to get sort indices
    # We'll take the first row of lons to determine the sorting order
    if lons.ndim == 2:
        lons_1d = lons[0, :]
    else:
        lons_1d = lons

    # Get the sorting indices
    i_sort = np.argsort(lons_1d)

    # Apply sorting to the 2D arrays across the longitude axis (axis=1)
    if lons.ndim == 2:
        lons = lons[:, i_sort]
        lats = lats[:, i_sort] # Sort lats too if it's a meshgrid
    else:
        lons = lons[i_sort]

    ws10m_data_v16 = ws10m_data_v16[:, i_sort]
    ws10m_data_v17 = ws10m_data_v17[:, i_sort]
    diff_data       = diff_data[:, i_sort]

    # Standard min/max
    print(f"v16  - Min: {ws10m_data_v16.min():.2f}, Max: {ws10m_data_v16.max():.2f}")
    print(f"v17  - Min: {ws10m_data_v17.min():.2f}, Max: {ws10m_data_v17.max():.2f}")
    print(f"Diff - Min: {diff_data.min():.2f}, Max: {diff_data.max():.2f}")

#########################################################

#########################################################

    # Create the 3-Panel Plot
    fig = plt.figure(figsize=(16, 12))

    # Define a 2x2 grid
    gs = gridspec.GridSpec(2, 2, figure=fig)

    # Define the specific normalization (Panels 1 & 2)
    #ws10m_norm = mcolors.Normalize(vmin=0, vmax=60)
    ws10m_levels = np.arange(0, 48, 2)

    # Key meteorological color transitions scaled from 0 to 46 m/s
    # (Position = wind_speed / 46.0)
    color_anchors = [
        (0.00, "#E0F3F8"),  #  0 m/s: Calm / Light air
        (0.17, "#4575B4"),  # ~8 m/s: Breeze (Moderate blue)
        (0.35, "#31A354"),  # 16 m/s: Advisory / Strong breeze (Green)
        (0.52, "#FEE08B"),  # 24 m/s: Gale / Warning (Pale yellow)
        (0.65, "#F46D43"),  # 30 m/s: Storm force (Orange-red)
        (0.72, "#D73027"),  # 33 m/s: Hurricane threshold / 74 mph (Red)
        (0.87, "#7A0177"),  # 40 m/s: Violent / Cat 2 (Magenta)
        (1.00, "#FFFFFF"),  # 46 m/s: ~100+ mph (White)
    ]

    cmap_smooth = LinearSegmentedColormap.from_list("nws_wind_smooth", color_anchors, N=256)
    norm_smooth = Normalize(vmin=0, vmax=46)

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
        {'data': ws10m_data_v16, 'cmap': cmap_smooth, 'norm': norm_smooth, 'levels': ws10m_levels, 'title': 'GFSv16 ws10m (m/s)'},
        {'data': ws10m_data_v17, 'cmap': cmap_smooth, 'norm': norm_smooth, 'levels': ws10m_levels, 'title': 'GFSv17 ws10m (m/s)'},
        {'data': diff_data,      'cmap': 'seismic',   'norm': diff_norm,   'levels': diff_levels,  'title': 'GFSv17 minus GFSv16 ws10m (m/s)'}
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
        ax.add_feature(cfeature.BORDERS, linewidth=1)
        ax.add_feature(cfeature.STATES, edgecolor='gray', linewidth=1.5, alpha=0.5)

        # Define domain
        if grid == "conus":
            ax.set_extent([-130, -65, 20, 56], crs=ccrs.PlateCarree())
        elif grid == "northamer":
            ax.set_extent([-170, -30, 10, 85], crs=ccrs.PlateCarree())

        # Check if we are on the third panel and apply special cmap
        if i == 2:
            current_cmap = white_center_cmap
        else:
            current_cmap = config['cmap']

        # Plot the shading
        if i < 2:
            im = ax.contourf(lons, lats, config['data'], 
                     levels=config['levels'],
                     norm=config['norm'], 
                     cmap=current_cmap,
                     transform=ccrs.PlateCarree(),
                     extend='max')
        else:
            im = ax.contourf(lons, lats, config['data'], 
                     levels=config['levels'],
                     norm=config['norm'],
                     cmap=current_cmap,
                     transform=ccrs.PlateCarree(),
                     extend='both')

        # Plot the contour lines
        # Only add lines if it's one of the MSLP panels (0 or 1)
        #if i < 2:
            #contours = ax.contour(lons, lats, config['data'], 
                              #levels=config['levels'], 
                              #colors='black', 
                              #linewidths=0.5, 
                              #transform=ccrs.PlateCarree())
            # Add labels to the lines (e.g., '1012')
            # Reduce padding (default is 4) to allow more labels to fit in tight spaces
            #ax.clabel(contours, inline=True, fontsize=8, fmt='%i', inline_spacing=1)

        # Colorbar and Titles
        plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.06, fraction=0.055)
        ax.set_title(config['title'], fontweight='bold', fontsize=14)

#################################################

    # Add a title and adjust layout to prevent overlapping
    plt.suptitle(f"10-m Wind Speed (ws10m) | Initialized: {init_dt.strftime('%Y-%m-%d %HZ')} (Fhr: {fhr_str}) | Valid: {valid_dt.strftime('%Y-%m-%d %HZ')}", fontsize=20)
    plt.tight_layout()
    plt.savefig(f"image_{img_counter}.png")

    img_counter = img_counter + 1
    print("img_counter:", img_counter)
