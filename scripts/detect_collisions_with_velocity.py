import pandas as pd
import math
import os
import csv

# ==========================================
# SETTINGS - CHANGE THESE TO TWEAK SIMULATION
# ==========================================
DISTANCE_THRESHOLD_M = 50000  # Set to 50000 (50km) to see more dots on the map
INPUT_FILE = "data/all_satellite_orbits.csv"
OUTPUT_FILE = "data/collision_risks_with_velocity.csv"
# ==========================================

print(f"Checking for satellites within {DISTANCE_THRESHOLD_M} meters...")

if not os.path.exists(INPUT_FILE):
    print(f"❌ Error: {INPUT_FILE} not found. Run GenerateAllOrbitsFromMetadata.py first.")
    exit()

df = pd.read_csv(INPUT_FILE)
df["Time (UTC)"] = pd.to_datetime(df["Time (UTC)"])

with open(OUTPUT_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Satellite 1", "Satellite 2", "Distance (m)"])

    for timestamp, group in df.groupby("Time (UTC)"):
        sats = group.values.tolist()
        for i in range(len(sats)):
            for j in range(i + 1, len(sats)):
                # 3D Distance Logic
                lat1, lon1, alt1 = sats[i][2], sats[i][3], sats[i][4]
                lat2, lon2, alt2 = sats[j][2], sats[j][3], sats[j][4]
                
                # Approximation of 3D Euclidean distance in meters
                d = math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2 + ((alt1-alt2)/100000)**2) * 111000
                
                if d < DISTANCE_THRESHOLD_M:
                    writer.writerow([timestamp, sats[i][0], sats[j][0], round(d, 2)])

print(f"✅ Analysis complete! Results saved to {OUTPUT_FILE}")