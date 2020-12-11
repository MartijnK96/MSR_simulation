#!/usr/bin/python3

# from transitions import Machine
import random
import numpy as np
import time
from datetime import time, date, datetime, timedelta
from scipy.spatial import distance
#import pandas as pd
import csv
import operator
from collections import namedtuple
import argparse
import sys
import json
import os
#from os.path import dirname as dir

class MSR(object):

    def __init__(self, id, init_location, location_dictionary, job_list):
        self.ID = id
        self.state = 'Park'
        # TODO: Obtain duration differently
        initial_task = msr1_joblist[0][0]
        self.duration = getSec(initial_task[1])
        self.location_mapping = location_dictionary
        self.location = init_location
        self.speed = 1  # Speed in m/s

        # Distance traveled in meters
        self.distance_traveled = 0

        # Time active - not used currently
        self.robot_clock = 0 
        # Time idle (parking + waiting + charging)
        self.idle_time = 0

        # Battery charge is initially X hours or Y Ah -- research more how to handle this
        self.charge = 1000

        # Initialize list of jobs to execute
        self.job_list = job_list
        # Initialize a counter that counts the number of sections swabbed
        self.job_counter = 0
    
    # TODO: Finish this function
    def transFunc(self,task,wallclock):
        # Input is a tuple with first element the name of the task
        task_name = task[0]
        
        if task_name == 'Move':
            # Execute the movetoLocation function
            duration = self.movetoLocation(task)
        elif task_name == 'Wait':
            duration = self.waitforsectionPause()
        elif task_name == 'Park':
            duration = self.Park(task)
        elif task_name == 'Charge':
            duration = self.chargeBattery()
        elif task_name == 'Calibrate':
            duration = self.calibratetoSection()
        elif task_name == 'Swab':
            try:
                sections = task[2]
                duration = self.Swab(sections)
            except IndexError:
                duration = self.Swab()
            
        print(wallclock.strftime("%H:%M:%S") + ": MSR" + str(self.ID) + " performed state " + task_name + 
              " at " + self.location + " with duration " + str(self.duration) + " seconds.")
            
    # TODO: Function should execute resursively if moving from a charging point - c1 - to a machine section - m11 - for instance
    def movetoLocation(self,task):
        global location_mapping
        self.state = 'Move'

        destination = task[1]
        
        # Retrieve current location
        curr_loc = self.location_mapping[self.location]
        self.location = destination
        # Retrieve desired location
        des_loc = self.location_mapping[destination]
        
        # Determine distance to be travelled
        distance = distance.euclidean(curr_loc, des_loc)

        # Compute duration for movement
        # TODO: Make more realistic for travelling shorter distances and accelerating/decelerating or handle some cases for traveling between machine sections
        moveto_duration = distance/self.speed
        
        # Increase relevant counters and change relevant class instance variables
        self.duration = moveto_duration
        self.robot_clock += moveto_duration
        
        return moveto_duration
    
        # Handle some cases to determine duration from section to section etc.

    def waitforsectionPause(self):
        self.state = 'Wait'

        # Determine duration of waiting action - uniform distribution
        lbound_wait = 4
        hbound_wait = 10
        wait_duration = random.uniform(lbound_wait, hbound_wait)
        self.duration = wait_duration
        self.robot_clock += wait_duration
        
        return wait_duration

    def Park(self, task):
        self.state = 'Park'

        park_duration = getSec(task[1]) - self.robot_clock
        self.idle_time += park_duration 
        self.duration = park_duration
        self.robot_clock += park_duration
        
        return park_duration

    def chargeBattery(self):
        self.state = 'Charge'

        # Determine duration of charging - modify later
        charge_duration = 30*60
        self.idle_time += charge_duration
        self.duration = charge_duration
        self.robot_clock += charge_duration
        
        return charge_duration

    def calibratetoSection(self):
        self.state = 'Calibrate'

        # Lower and higher bound of calibration time in seconds
        lbound_calibrate = 8
        hbound_calibrate = 12
        calibrate_duration = random.uniform(lbound_calibrate, hbound_calibrate)
        self.duration = calibrate_duration
        self.robot_clock += calibrate_duration
        
        return calibrate_duration

    def Swab(self, sections=3):
        self.state = 'Swabbing'
        mean_3sec = 12
        if sections == 3:  # If number of sections equals 3 the swabbing duration is 12s
            swab_duration = np.random.normal(mean_3sec,0.1,1)[0]
        else:
            mean = (sections/3)*mean_3sec
            swab_duration = np.random.normal(mean,0.1,1)[0]
        
        # Increase relevant counters and change relevant class instance variables    
        self.duration = swab_duration
        self.robot_clock += swab_duration
        self.job_counter += 1

        return swab_duration


def getSec(s):
    L = s.split(':')
    if len(L) == 1:
        return L[0]
    elif len(L) == 2:
        datee = datetime.strptime(s, "%M:%S")
        return datee.minute * 60 + datee.second
    elif len(L) == 3:
        datee = datetime.strptime(s, "%H:%M:%S")
        return datee.hour * 3600 + datee.minute * 60 + datee.second


def locationdictfromCSV(coordinatefile_name):
    project_dir = os.path.dirname(os.path.dirname((__file__)))
    print(project_dir)
    relative_path = 'input/coordata/{}'.format(coordinatefile_name)
    print(relative_path)
    coordinatefile = os.path.join(project_dir, relative_path)
    
    f = open(coordinatefile, 'r')
    reader = csv.reader(f)

    location_mapping = {}

    for row in reader:
        location_mapping[row[0]] = [float(x) for x in row[1:]]

    return location_mapping

def getjobDict(jobfile_name):
    project_dir = os.path.dirname(os.path.dirname((__file__)))
    relative_path =  'input/joblist/{}'.format(jobfile_name)
    jobfile = os.path.join(project_dir, relative_path)
    
    with open(jobfile, 'r') as fjson:
        joblist_dict = json.load(fjson)
        
    for joblist in joblist_dict:
        for idx, job in enumerate(joblist_dict[joblist]):
            joblist_dict[joblist][idx] = [tuple(subtask) for subtask in job]
            
    return joblist_dict
    
def parseArgs():
    """
    Argument parser function.

    Returns:
        args (argument list): input arguments
    """
    
    parser = argparse.ArgumentParser(description='Input filenames for input files.')
    parser.add_argument('-cf','--coordinatefile',type=str, default='coordinate_points.csv', help='Name of the .csv file containing the coordinate mapping.')
    parser.add_argument('-jf','--jobfile',type=str, default='job_list.json', help='Name of the .json file containing the jobs for the MSR robots.')
    parser.add_argument('-il','--initlocs', nargs="+", default=['p1','p2'], help='Initial locations for the robots.')
    parser.add_argument('-r','--robots', type=int, default=2, help='Number of robots.')
    
    args = parser.parse_args()
    
    return args
    

if __name__ == '__main__':
    # Get command line arguments and generate location-mapping dict. and joblist dict.
    args = parseArgs()
    coordinatefile = args.coordinatefile
    jobfile = args.jobfile
    initloc_list = args.initlocs
    num_robots = args.robots
    
    #directory = dir(dir((__file__)))
    #print(directory)
    location_mapping = locationdictfromCSV(coordinatefile)
    joblist_dict = getjobDict(jobfile)
    
    # Initialize wallclock time - use a dummy date
    # Start simulation at midnight
    wallclock = datetime(2020,12,4,0,0,0,0)

    # Assign an initial location to both robots
    # initloc_msr1 = 'p1'
    # initloc_msr2 = 'p2'
    
    robot_list = [MSR(*i,initloc_list[i],location_mapping,joblist_dict[i]) for i in range(1,num_robots+1)]
    print(objs)
    # # Create i robot objects with different initial locations and jobs
    # msr1 = MSR(1, initloc_msr1, location_mapping, msr1_joblist)
    # msr2 = MSR(2, initloc_msr2, location_mapping, msr2_joblist)
    
    # # Make list of robot objects
    # robot_list = [msr1, msr2]

    num_done = 0
    #while (msr1.job_list or msr2.job_list) and (num_done < num_robots):
    while (robot.job_list for robot in robot_list) and (num_done < num_robots):
        # Find robot with shortest remaining job duration, and the smallest remaining duration itself
        robot_list_sorted = sorted(robot_list, key=operator.attrgetter('duration'))
        smallest_duration = robot_list_sorted[0].duration
        
        wallclock += timedelta(seconds=smallest_duration)
            
        for robot in robot_list:
            if robot.duration == smallest_duration and robot.job_list:
                # Execute task and remove task from joblist for this robot
                # Check size of list and remove from joblist if empty
                task = robot.job_list[0].pop(0)
                robot.transFunc(task,wallclock)
                
                # If first list is empty delete is from job_list
                if not robot.job_list[0]:
                    del robot.job_list[0]

            else: 
                robot.duration -= smallest_duration
                
        for robot in robot_list:
            if not robot.job_list:
                robot_list.remove(robot)
                num_done += 1            
                
        