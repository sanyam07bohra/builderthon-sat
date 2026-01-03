import pandas as pd
from skyfield.api import load, EarthSatellite, wgs84
import csv
import os

# Load raw satellite metadata
metadata_path = "data/starlink_metadata.csv"
if not os.path.exists(metadata_path):
    print("Error: data/starlink_metadata.csv not found!")
    exit()

df = pd.read_csv(metadata_path).head(100) # Processing first 100 for speed
ts = load.timescale()
output_path = "data/all_satellite_orbits.csv"

with open(output_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Satellite Name", "Time (UTC)", "Latitude", "Longitude", "Altitude (m)"])

    for _, row in df.iterrows():
        try:
            # Construct TLE (Two-Line Element) from CSV data
            line1 = f"1 {int(row['NORAD_CAT_ID']):05d}U {row['OBJECT_ID'].replace('-', ''):<8} 25208.12546533 -.00001777  00000+0 -10041-3 0  9999"
            line2 = f"2 {int(row['NORAD_CAT_ID']):05d} {row['INCLINATION']:8.4f} {row['RA_OF_ASC_NODE']:8.4f} {int(float(row['ECCENTRICITY'])*1e7):07d} {row['ARG_OF_PERICENTER']:8.4f} {row['MEAN_ANOMALY']:8.4f} {row['MEAN_MOTION']:11.8f}00001"
            
            sat = EarthSatellite(line1, line2, row["OBJECT_NAME"], ts)
            # Calculate positions for the next 24 hours in 10-minute steps
            for i in range(0, 1440, 10):
                t = ts.now() + i / (60 * 24)
                subpoint = wgs84.subpoint(sat.at(t))
                writer.writerow([row["OBJECT_NAME"], t.utc_iso(), subpoint.latitude.degrees, subpoint.longitude.degrees, subpoint.elevation.m])
        except Exception: continue
print("Done! Positions saved to data/all_satellite_orbits.csv")