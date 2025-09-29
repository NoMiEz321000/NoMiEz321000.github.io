import math
from sklearn.cluster import KMeans
import pandas as pd
from sklearn import mixture
from sklearn.metrics import *
import numpy as np
import matplotlib.pyplot as plt



df = pd.read_csv('day1.csv')
callsign = df.callsign.unique()

lat = []
lon = []
baroaltitude = []

last_lat =[]
last_lon = []
last_baroaltitude = []

fourDcombine = []

plt.figure(1)
tatalcallsignlanding = 0

for i in range(len(callsign)):
    #print(callsign[i])
    if(str(callsign[i]) != 'nan'):
        focus_row = df.loc[df['callsign'] == callsign[i]]

        temptime = focus_row["time"].tolist()
        templat = focus_row["lat"].tolist()
        templon = focus_row["lon"].tolist()
        temp = focus_row["baroaltitude"].tolist()
        tempheading = focus_row["heading"].tolist()
        tempvel = focus_row["velocity"].tolist()

        last_lat_ = templat[-1]
        last_lat.append(last_lat_)
        last_lon_ = templon[-1]
        last_lon.append(last_lon_)
        last_baroaltitude_ = temp[-1]
        last_baroaltitude.append(last_baroaltitude_)


        if (templat[-1]>13.6) and (templat[-1]<13.930) and (templon[-1]>100.7) and (templon[-1]<100.8):

            temp_time = abs(temptime[-1] - temptime[0])
            temp_dist = 0

            for j in range(len(templat)-1):
                temp_dist += math.sqrt(( templat[j]- templat[j+1]) ** 2 + (templon[j] - templon[j+1]) ** 2+ (temp[j] - temp[j+1]) ** 2)
            if (str(temp_dist) != 'nan') and (str(temp_time) != 'nan') :

                plt.scatter(templon,templat,color='b', s=0.5)
                lat.append(templat)
                lon.append(templon)
                baroaltitude.append(temp)

                fourDcombine.append([templat[0],templon[0],templon[-1],templat[-1],temptime[0],temptime[-1],temp_dist,temp_time])
                print("Keep callsign: " + str(i) + "_" + str(callsign[i]))
                print(str(callsign[i]) + " 3Ddist = " + str(temp_dist) + " Time Diff " + str(temp_time))
                tatalcallsignlanding += 1



plt.ylabel('Latitude')
plt.xlabel('Longitude')
plt.title("2D view trajectory")
#plt.savefig('2Dviewtrajectory.png', dpi=300,bbox_inches='tight')


plt.show()