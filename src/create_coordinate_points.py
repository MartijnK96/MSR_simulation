#!/usr/bin/env python3

import sys
import csv

try:
    machines, sections, charging_stations = (int(x) for x in sys.argv[1:])
except:
    machines, sections, charging_stations = 4, 8, 2

type(machines)

wall_to_IS = 5090
width_IS = 5150
distance_IS = 6610
length_IS = 7532
distance_SEC = 7532/(sections+1)
separation_SEC = 300

with open("coordinate_points.csv", "w+") as f:
    for i in range(1,machines+1):
        for i in range(1,sections+1):
            
