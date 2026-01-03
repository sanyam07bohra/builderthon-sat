import os
import pandas as pd

# 1. Get the directory where THIS script is saved
script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Paths for Input and Output
input_csv = os.path.join(script_dir, "..", "data", "collision_risks_with_velocity.csv")
orbit_path = os.path.join(script_dir, "..", "data", "all_satellite_orbits.csv")
output_path = os.path.join(script_dir, "..", "data", "persistent_risks.csv")

# 3. Check if the detection file exists
if os.path.exists(input_csv):
    print(f"✅ Found detection data at: {input_csv}")
    df = pd.read_csv(input_csv)
else:
    print(f"❌ Error: {input_csv} is missing. Run 'detect_collisions_with_velocity.py' first.")
    exit()

# 4. Processing logic
pair_history = {}
risk_rows = []
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

for _, row in df.iterrows():
    pair_key = tuple(sorted((row["Satellite 1"], row["Satellite 2"])))
    last_time, streak = pair_history.get(pair_key, (None, 0))
    
    # Calculate streak (persistent risk)
    if last_time and (row["Timestamp"] - last_time).total_seconds() <= 900:
        streak += 1
    else:
        streak = 1
    
    pair_history[pair_key] = (row["Timestamp"], streak)
    
    # Risk Score formula: (1/distance) * streak
    risk_score = (1 / (float(row["Distance (m)"]) + 1)) * (1 + streak)
    risk_rows.append([row["Timestamp"], row["Satellite 1"], row["Satellite 2"], row["Distance (m)"], streak, risk_score])

# 5. Merge GPS positions for the Dashboard Map
output_df = pd.DataFrame(risk_rows, columns=["Timestamp", "Satellite 1", "Satellite 2", "Distance (m)", "Streak", "Risk Score"])

if os.path.exists(orbit_path):
    orbit_df = pd.read_csv(orbit_path, parse_dates=["Time (UTC)"])
    # Link risk data to coordinates
    merged = output_df.merge(
        orbit_df[["Satellite Name", "Time (UTC)", "Latitude", "Longitude"]],
        left_on=["Satellite 1", "Timestamp"],
        right_on=["Satellite Name", "Time (UTC)"],
        how="left"
    ).drop(columns=["Satellite Name", "Time (UTC)"])
    
    merged.to_csv(output_path, index=False)
    print(f"✅ Success! Position-enhanced data saved to {output_path}")
else:
    output_df.to_csv(output_path, index=False)
    print(f"⚠️ Saved risk scores, but could not find Lat/Lon data for the map.")