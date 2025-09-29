import pandas as pd
import numpy as np
from math import sin, cos, sqrt, atan2, radians
from tqdm import tqdm


# --- Vectorized Haversine distance in nautical miles ---
def haversine_nm_vec(lat, lon):
    """
    lat, lon: numpy arrays in degrees
    Returns a distance matrix [n x n] in nautical miles
    """
    R = 6371.0  # Earth radius in km

    # convert degrees to radians
    lat = np.radians(lat)
    lon = np.radians(lon)

    dlat = lat[:, None] - lat[None, :]
    dlon = lon[:, None] - lon[None, :]

    a = np.sin(dlat / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    dist_km = R * c
    return dist_km / 1.852  # convert km → nautical miles


# --- Conflict check between all pairs in one timestamp ---
def check_conflicts(lat, lon, alt_m, callsign, time, conflicts, conflict_times):
    n = len(lat)
    if n < 2:
        return

    # Compute all pairwise horizontal distances
    horiz_nm = haversine_nm_vec(np.array(lat), np.array(lon))

    # Compute vertical separation in feet
    alt_ft = np.array(alt_m) * 3.28084
    vert_ft = np.abs(alt_ft[:, None] - alt_ft[None, :])

    # Mask for conflicts (ignore self-comparisons with np.triu)
    conflict_mask = (horiz_nm < 3) & (vert_ft < 1000)
    conflict_mask = np.triu(conflict_mask, k=1)  # keep upper triangle (i<j)

    # Extract indices of conflicts
    idx_i, idx_j = np.where(conflict_mask)

    for i, j in zip(idx_i, idx_j):
        conflicts.append([callsign[i], callsign[j]])
        conflict_times.append(time)


# --- Remove duplicates but keep order ---
def unique(lst):
    seen = []
    for x in lst:
        if x not in seen:
            seen.append(x)
    return seen


# === MAIN ===
data = pd.read_csv("day1.csv").dropna()
times = data["time"].unique()

conflicts = []
conflict_times = []

# Loop through each timestamp with tqdm progress bar
for t in tqdm(times, desc="Checking conflicts by time"):
    focus = data.loc[data['time'] == t]
    lat = focus["lat"].to_numpy()
    lon = focus["lon"].to_numpy()
    alt_m = focus["baroaltitude"].to_numpy()
    callsign = focus["callsign"].to_numpy()

    check_conflicts(lat, lon, alt_m, callsign, t, conflicts, conflict_times)

# Deduplicate conflict pairs
unique_conflicts = unique(conflicts)

# --- Print results ---
print("\nAircraft conflicts detected:\n")
for pair in unique_conflicts:
    print(f"{pair[0]}  and  {pair[1]}")
    for k in range(len(conflicts)):
        if conflicts[k] == pair:
            print(f"  At time: {conflict_times[k]}")
            print("--------------------------------------------------\n")
            break

print("\n=== Results Summary ===")
print(f"Total aircraft in dataset: {data['callsign'].nunique()}")
print(f"Total conflicts detected: {len(conflicts)}")
print(f"Total unique conflict : {len(unique_conflicts)}")
