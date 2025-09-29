import pandas as pd
from math import sin, cos, sqrt, atan2, radians
from tqdm import tqdm

data = pd.read_csv("day1.csv").dropna()
times = data["time"].unique()
conflicts = []
conflict_times = []

def haversine_nm(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    dist_km = R * c
    return dist_km / 1.852

def check_conflicts(lat, lon, alt_m, callsign, time, conflicts, conflict_times):
    for i in range(len(lat)):
        for j in range(i+1, len(lat)):
            horiz_nm = haversine_nm(lat[i], lon[i], lat[j], lon[j])
            vert_ft = abs(alt_m[i] - alt_m[j]) * 3.28084
            if horiz_nm < 3 and vert_ft < 1000:
                conflicts.append([callsign[i], callsign[j]])
                conflict_times.append(time)

def unique(lst):
    seen = []
    for x in lst:
        if x not in seen:
            seen.append(x)
    return seen

for t in tqdm(times, desc="Checking conflicts by time"):
    focus = data.loc[data['time'] == t]
    lat = focus["lat"].tolist()
    lon = focus["lon"].tolist()
    alt_m = focus["baroaltitude"].tolist()
    callsign = focus["callsign"].tolist()
    check_conflicts(lat, lon, alt_m, callsign, t, conflicts, conflict_times)

unique_conflicts = unique(conflicts)

print("\nAircraft conflicts detected:\n")
for pair in unique_conflicts:
    print(f"{pair[0]}  and  {pair[1]}")
    for k in range(len(conflicts)):
        if conflicts[k] == pair:
            print(f"  At time: {conflict_times[k]}")
            print("--------------------------------------------------\n")
            break

print("=== Results Summary ===")
print(f"Total aircraft in dataset: {data['callsign'].nunique()}")
print(f"Total conflicts detected: {len(conflicts)}")
print(f"Total unique conflict : {len(unique_conflicts)}")
