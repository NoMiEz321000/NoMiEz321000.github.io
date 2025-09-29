import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy.spatial import cKDTree

# read dataset
data = pd.read_csv("day1.csv")
data = data.dropna(subset=["lat", "lon", "baroaltitude", "callsign"])

# convert degrees to radians for haversine
data["lat_rad"] = np.radians(data["lat"])
data["lon_rad"] = np.radians(data["lon"])

# constants
EARTH_RADIUS_KM = 6371.0
NM_TO_KM = 1.852
HORIZ_LIMIT = 3 * NM_TO_KM   # 3 NM in km
VERT_LIMIT = 1000 / 3.28084  # 1000 ft in meters → to baroaltitude units (meters)

# result storage
conflicts = []
conflict_times = []

# loop through each timestamp
for t in tqdm(data["time"].unique(), desc="Checking conflicts by time"):
    group = data[data["time"] == t]

    if len(group) < 2:
        continue

    # build KDTree on lat/lon (projected to 3D Cartesian for distance calc)
    x = EARTH_RADIUS_KM * np.cos(group["lat_rad"]) * np.cos(group["lon_rad"])
    y = EARTH_RADIUS_KM * np.cos(group["lat_rad"]) * np.sin(group["lon_rad"])
    z = EARTH_RADIUS_KM * np.sin(group["lat_rad"])
    coords = np.vstack((x, y, z)).T

    tree = cKDTree(coords)

    # query neighbors within 3 NM
    pairs = tree.query_pairs(HORIZ_LIMIT / EARTH_RADIUS_KM)  # angular radius

    for i, j in pairs:
        alt_diff = abs(group.iloc[i]["baroaltitude"] - group.iloc[j]["baroaltitude"])
        if alt_diff < VERT_LIMIT:
            conflicts.append((group.iloc[i]["callsign"], group.iloc[j]["callsign"]))
            conflict_times.append(t)

# unique conflict pairs
unique_conflicts = list(set(tuple(sorted(pair)) for pair in conflicts))

print("\n=== Results ===")
print(f"Total aircraft in dataset: {data['callsign'].nunique()}")
print(f"Total conflicts detected: {len(conflicts)}")
print(f"Total unique conflict pairs: {len(unique_conflicts)}")

for a, b in unique_conflicts:
    print(f"{a} ↔ {b}")
