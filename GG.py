import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy.spatial import cKDTree
from math import sin, cos, sqrt, atan2, radians

# read dataset
data = pd.read_csv("day1.csv")
data = data.dropna(subset=["lat", "lon", "baroaltitude", "callsign"])

# convert to radians
data["lat_rad"] = data["lat"].apply(radians)
data["lon_rad"] = data["lon"].apply(radians)

# constants
EARTH_RADIUS_KM = 6371.0
NM_TO_KM = 1.852
HORIZ_LIMIT = 3 * NM_TO_KM   # 3 NM → km
VERT_LIMIT = 1000 / 3.28084  # 1000 ft → meters

# storage
conflicts = []
conflict_times = []

# loop through each timestamp
for t in tqdm(data["time"].unique(), desc="Checking conflicts by time"):
    group = data[data["time"] == t].reset_index(drop=True)

    if len(group) < 2:
        continue

    # project lat/lon onto 3D Cartesian sphere (better visualization than pure np.cos/sin)
    x = [EARTH_RADIUS_KM * cos(lat) * cos(lon) for lat, lon in zip(group["lat_rad"], group["lon_rad"])]
    y = [EARTH_RADIUS_KM * cos(lat) * sin(lon) for lat, lon in zip(group["lat_rad"], group["lon_rad"])]
    z = [EARTH_RADIUS_KM * sin(lat) for lat in group["lat_rad"]]

    coords = np.vstack((x, y, z)).T
    tree = cKDTree(coords)

    # query neighbors within angular distance equivalent to 3 NM
    pairs = tree.query_pairs(HORIZ_LIMIT / EARTH_RADIUS_KM)

    for i, j in pairs:
        alt_diff = abs(group.loc[i,"baroaltitude"] - group.loc[j,"baroaltitude"])
        if alt_diff < VERT_LIMIT:
            conflicts.append((group.loc[i,"callsign"], group.loc[j,"callsign"]))
            conflict_times.append(t)

            # detailed conflict output
            print(f"{group.loc[i,'callsign']}   and   {group.loc[j,'callsign']}")
            print(f"At time: {t}")
            print("----------------------------------------------------\n")

# unique conflict pairs
unique_conflicts = list(set(tuple(sorted(pair)) for pair in conflicts))

print("\n=== Results Summary ===")
print(f"Total aircraft in dataset: {data['callsign'].nunique()}")
print(f"Total conflicts detected: {len(conflicts)}")
print(f"Total unique conflict pairs: {len(unique_conflicts)}")

for a, b in unique_conflicts:
    print(f"{a} ↔ {b}")
