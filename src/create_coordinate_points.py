#!/usr/bin/env python3

import sys
import csv
import argparse
import os
from os.path import dirname as dir


def getArgs():
    """
    Get command line arguments.
    """
    try:
        machines, sections, charging_stations = (int(x) for x in sys.argv[1:])
    except:
        machines, sections, charging_stations = 4, 8, 2
        
    return machines, sections, charging_stations

def parseArgs():

    """
    Argument parser function.

    Returns:
        args (argument list): input arguments
    """
    
    parser = argparse.ArgumentParser(description='Generate .csv file with coordinates.')
    parser.add_argument('-f','--filename',type=str, default='coordinate_points.csv', help='Name of the CSV file to write to.')
    parser.add_argument('-m','--machines', type=int, default=4, help='Number of machines.')
    parser.add_argument('-s','--sections', type=int, default=8, help='Number of sections per machine.')
    parser.add_argument('-c','--chargers', type=int, default=2, help='Number of sections per machine.')

    args = parser.parse_args()
    
    return args

def writetoCSV(filename, machines, sections, charging_station):
    # Define parameters 
    # TODO: get from file
    space_left = 10000
    wall_to_IS = 5090
    width_IS = 5150
    distance_IS = 6610
    length_IS = 7532
    #distance_SEC = 7532/(sections+1)
    distance_SEC = 7532/(8+1)
    separation_SEC = 300
    
    project_dir = dir(dir((__file__)))
    relative_path = 'input/coordata/{}'.format(filename)
    file_path = os.path.join(project_dir, relative_path)
    
    with open(file_path, "w+") as f:
        writer = csv.writer(f)

        for i in range(machines):
            label = "p{}".format(i+1)
            x_coor_mm = space_left-2500
            x_coor_m = x_coor_mm/1000
            y_coor_mm = wall_to_IS + i*(width_IS+distance_IS)
            y_coor_m = y_coor_mm/1000
            writer.writerow([label, x_coor_m, y_coor_m])

        for i in range(machines):
            for j in range(sections):
                label = "m{}{}".format(i+1,j+1)
                x_coor_mm = space_left + (distance_SEC*(j+1))
                x_coor_m = x_coor_mm/1000
                y_coor_mm = wall_to_IS + i*(width_IS+distance_IS)
                y_coor_m = y_coor_mm/1000
                writer.writerow([label, x_coor_m, y_coor_m])
                
        
    

if __name__ == "__main__":
    # Getting arguments 
    machines, sections, charging_station = getArgs()
    
    args = parseArgs()
    filename = args.filename
    machines = args.machines
    sections = args.sections
    charging_station = args.chargers
    
    # Writing to CSV file with filename specified in the command line
    writetoCSV(filename, machines, sections, charging_station)
    
