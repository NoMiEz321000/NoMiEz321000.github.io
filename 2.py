import pandas as pd
from math import sin, cos, sqrt, atan2, radians
from tqdm import tqdm

# read dataset
data = pd.read_csv("day1.csv")
data = data.dropna(subset=["lat", "lon", "baroaltitude", "callsign"])

# constants
EARTH_RADIUS_KM = 6371.0
NM_TO_KM = 1.852
HORIZ_LIMIT = 3 * NM_TO_KM   # 3 NM in km (~5.556 km)
VERT_LIMIT = 1000 / 3.28084  # 1000 ft in meters

# result storage
conflicts = []
conflict_times = []

# haversine distance in km
def horiz_dist(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return EARTH_RADIUS_KM * c

# loop through each timestamp
for t in tqdm(data["time"].unique(), desc="Checking conflicts by time"):
    group = data[data["time"] == t].reset_index(drop=True)

    if len(group) < 2:
        continue

    for i in range(len(group)):
        for j in range(i+1, len(group)):
            dist = horiz_dist(group.loc[i,"lat"], group.loc[i,"lon"],
                              group.loc[j,"lat"], group.loc[j,"lon"])
            alt_diff = abs(group.loc[i,"baroaltitude"] - group.loc[j,"baroaltitude"])

            if dist < HORIZ_LIMIT and alt_diff < VERT_LIMIT:
                conflicts.append((group.loc[i,"callsign"], group.loc[j,"callsign"]))
                conflict_times.append(t)
                # detailed conflict info
                print(f"{group.loc[i,'callsign']}   and   {group.loc[j,'callsign']}")
                print(f"At time: {t}")
                print("----------------------------------------------------\n")

# unique conflict pairs
unique_conflicts = list(set(tuple(sorted(pair)) for pair in conflicts))

print("\n=== Results Summary ===")
print(f"Total aircraft in dataset: {data['callsign'].nunique()}")
print(f"Total conflicts detected: {len(conflicts)}")
print(f"Total unique conflict pairs: {len(unique_conflicts)}")
