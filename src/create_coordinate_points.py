#!/usr/bin/env python3

import sys
import csv

try:
    machines, sections, charging_stations = (int(x) for x in sys.argv[1:])
except:
    machines, sections, charging_stations = 4, 8, 2

space_left = 10000
wall_to_IS = 5090
width_IS = 5150
distance_IS = 6610
length_IS = 7532
distance_SEC = 7532/(sections+1)
separation_SEC = 300

with open("coordinate_points.csv", "w+") as f:
    #writer = csv.DictWriter(f, fieldnames=["label", "x", "y"])
    #writer.writeheader()
    writer = csv.writer(f)

    for i in range(machines):
        label = "p" + str(i+1)
        x_coor_mm = space_left-2500
        x_coor_m = x_coor_mm/1000
        y_coor_mm = wall_to_IS + i*(width_IS+distance_IS)
        y_coor_m = y_coor_mm/1000
        writer.writerow([label, x_coor_m, y_coor_m])

    for i in range(machines):
        for j in range(sections):
            label = "m" + str(i+1) + str(j+1)
            x_coor_mm = space_left + (distance_SEC*(j+1))
            x_coor_m = x_coor_mm/1000
            y_coor_mm = wall_to_IS + i*(width_IS+distance_IS)
            y_coor_m = y_coor_mm/1000
            writer.writerow([label, x_coor_m, y_coor_m])
