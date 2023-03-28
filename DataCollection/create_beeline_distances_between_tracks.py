import json
import pickle

import geopy.distance
import numpy as np

with open("../data/locations.json", "r") as f:
    locations = json.load(f)

n = len(locations)
distances = np.zeros((n, n))

for location_1 in locations.values():
    for location_2 in locations.values():
        beeline_distance = 0

        id1 = location_1["location_id"]
        id2 = location_2["location_id"]
        if id1 != id2:
            coords_1 = (location_1["latitude"], location_1["longitude"])
            coords_2 = (location_2["latitude"], location_2["longitude"])

            beeline_distance = geopy.distance.geodesic(coords_1, coords_2).km

        distances[id1][id2] = beeline_distance

print(distances)

pickle.dump(distances, open("../data/beeline_distances.bin", "wb"))
