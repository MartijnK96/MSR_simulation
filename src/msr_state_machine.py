#!/usr/bin/python3

# For calculating state durations
import random
import numpy as np
from scipy.spatial import distance

# For handling time
import time as tyme
from datetime import time, date, datetime, timedelta

# For writing/reading data and creating plots
import csv
import json
import pandas as pd
import matplotlib.pyplot as plt
#from matplotlib.pyplot import pie, axis, show

# For getting and processing command line arguments
import argparse
import sys
import os

import operator
from collections import namedtuple

class MSR(object):

    def __init__(self, id, init_location, location_dictionary, job_list):
        self.ID = id
        self.name = 'MSR{}'.format(id)
        self.state = 'Park'
        self.location_mapping = location_dictionary
        self.location = init_location
        self.previouslocation = ''
        self.max_speed = 1  # Speed in m/s
        self.adapted_speed = 0.3 # Speed for moving between two adjacent sections
        
        #Obtain initial task + duration
        initial_task = job_list[0][0]
        self.duration = getSec(initial_task[1])

        # Distance traveled in meters
        self.distance_traveled = 0

        # Time active
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
        # Input is a tuple with first element the name of the task and second element the location of the task
        task_name = task[0]
        task_location = task[1]
        
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
        self.state = 'Move'

        destination = task[1]
        
        # Retrieve current location
        curr_loc = self.location_mapping[self.location]
        # Retrieve desired location
        des_loc = self.location_mapping[destination]
        
        # Determine distance to be travelled
        dist = distance.euclidean(curr_loc, des_loc)
        
        # Compute duration for movement
        # Handle some cases to determine duration from section to section etc.
        # TODO: Make more realistic for travelling shorter distances and accelerating/decelerating or handle some cases for traveling between machine sections
        if (self.location[0] == destination[0]):
            moveto_duration = dist/self.adapted_speed
        else:
            moveto_duration = dist/self.max_speed
        
        # Increase relevant counters and change relevant class instance variables
        self.duration = moveto_duration
        self.previouslocation = self.location
        self.location = destination
        self.robot_clock += moveto_duration
        self.distance_traveled += dist
        
        return moveto_duration

    def waitforsectionPause(self):
        self.state = 'Wait'

        # Determine duration of waiting action - uniform distribution
        lbound_wait = 4
        hbound_wait = 10
        wait_duration = random.uniform(lbound_wait, hbound_wait)
        
        # Increase relevant counters and change relevant class instance variables
        self.duration = wait_duration
        self.previouslocation = self.location
        self.idle_time += wait_duration
        self.robot_clock += wait_duration
        
        return wait_duration

    def Park(self, task):
        self.state = 'Park'

        park_duration = getSec(task[1]) - self.robot_clock
        
        # Increase relevant counters and change relevant class instance variables
        self.duration = park_duration
        self.previouslocation = self.location
        self.idle_time += park_duration 
        self.robot_clock += park_duration
        
        return park_duration

    def chargeBattery(self):
        self.state = 'Charge'

        # Determine duration of charging - modify later
        charge_duration = 30*60
        
        # Increase relevant counters and change relevant class instance variables
        self.duration = charge_duration
        self.previouslocation = self.location
        self.idle_time += charge_duration
        self.robot_clock += charge_duration
        
        return charge_duration

    def calibratetoSection(self):
        self.state = 'Calibrate'

        # Lower and higher bound of calibration time in seconds
        lbound_calibrate = 8
        hbound_calibrate = 12
        calibrate_duration = random.uniform(lbound_calibrate, hbound_calibrate)
        
        # Increase relevant counters and change relevant class instance variables
        self.duration = calibrate_duration
        self.previouslocation = self.location
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
        self.previouslocation = self.location
        self.robot_clock += swab_duration
        self.job_counter += 1

        return swab_duration

def getSec(ts):
    """
    Function that takes timestring ('hh:mm:ss', 'mm:ss') and returns seconds.

    Args:
        ts (string): Time string.

    Returns:
        Time string converted to seconds (float64)
    """
    L = ts.split(':')
    if len(L) == 1:
        return L[0]
    elif len(L) == 2:
        datee = datetime.strptime(ts, "%M:%S")
        return datee.minute * 60 + datee.second
    elif len(L) == 3:
        datee = datetime.strptime(ts, "%H:%M:%S")
        return datee.hour * 3600 + datee.minute * 60 + datee.second


def locationdictfromCSV(coordinatefile_name):
    """
    Function that takes as input the filename of the .csv file containing location labels and coordinates 
    and returns a dicionary containing them. 
    
    Args:
        coordinatefile_name (str): Name of the .csv file

    Returns:
        location_mapping (dict): Dictionary of location labels as keys, and coordinates as arrays.
    """
    
    project_dir = os.path.dirname(os.path.dirname((__file__)))
    relative_path = 'input/coordata/{}'.format(coordinatefile_name)
    coordinatefile = os.path.join(project_dir, relative_path)
    
    f = open(coordinatefile, 'r')
    reader = csv.reader(f)

    location_mapping = {}

    for row in reader:
        location_mapping[row[0]] = [float(x) for x in row[1:]]

    return location_mapping

def getjobDict(jobfile_name):
    """
    Function that takes as input the filename of the .json file containing joblists of the MSR robots 
    and returns a dicionary containing them. 
    
    Args:
        jobfile_name (str): Name of the .json file

    Returns:
        joblist_dict (dict): Dictionary 
    """
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
    parser.add_argument('-of','--outputfile',type=str, default='sim_output.csv', help='Name of the .csv file containing outputs for all MSR robots.')
    parser.add_argument('-il','--initlocs', nargs="+", default=['p1','p2'], help='Initial locations for the robots.')
    parser.add_argument('-r','--robots', type=int, default=2, help='Number of robots.')
    
    args = parser.parse_args()
    
    return args

def Simulate(num_robots, robot_list, wallclock,outfile_name):
    num_done = 0
    while (robot.job_list for robot in robot_list) and (num_done < num_robots):
        # Find robot with shortest remaining job duration, and the smallest remaining duration itself
        robot_list_sorted = sorted(robot_list, key=operator.attrgetter('duration'))
        smallest_duration = robot_list_sorted[0].duration
        
        wallclock += timedelta(seconds=smallest_duration)
            
        for robot in robot_list:
            if robot.duration == smallest_duration and robot.job_list:
                # Execute task and remove task from joblist for this robot
                task = robot.job_list[0].pop(0)
                robot.transFunc(task,wallclock)
                
                # Call method for writing to CSV file
                writeoutputtoCSV(wallclock,robot,outfile_name)
                
                # If first list is empty delete is from job_list
                if not robot.job_list[0]:
                    del robot.job_list[0]

            else: 
                robot.duration -= smallest_duration
                
        for robot in robot_list:
            if not robot.job_list:
                robot_list.remove(robot)
                num_done += 1      

def writeoutputtoCSV(wallclock,robot,outfile_name):
    """
    Function that writes lines of output to .csv file on every state transition.

    Args:
        robot ([type]): [description]
    """
    
    project_dir = os.path.dirname(os.path.dirname((__file__)))
    relative_path = 'output/main/{}'.format(outfile_name)
    outfile = os.path.join(project_dir, relative_path)
    
    csvRow = [str(wallclock.time()), robot.name, robot.state, robot.duration, robot.previouslocation, robot.location, robot.distance_traveled, robot.idle_time, robot.robot_clock]
    with open(outfile,'a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csvRow)
        
def createPlots(outfile_name, num_robots):
    """
    Function to create plots.

    Args:
        outfile_name (string): Name of the .csv output file to read from. 
    """
    project_dir = os.path.dirname(os.path.dirname((__file__)))
    relative_path = 'output/main/{}'.format(outfile_name)
    outfile = os.path.join(project_dir, relative_path)
    robotname_list = ['MSR{}'.format(i) for i in range(1,num_robots+1)]
    df = pd.read_csv(outfile)
    
    for idx, name in enumerate(robotname_list):
        state_sums = df[df.Robot == name].groupby('State')['Duration'].sum()
        plt.figure(idx)
        plt.title('MSR{}: time spent in states'.format(idx))
        plt.axis('equal');
        plt.pie(state_sums, labels=state_sums.index);
        
    plt.show()

if __name__ == '__main__':
    
    # Get command line arguments and generate location-mapping dict. and joblist dict.
    args = parseArgs()
    coordinatefile = args.coordinatefile
    jobfile = args.jobfile
    initloc_list = args.initlocs
    num_robots = args.robots
    outputfile = args.outputfile

    # Get location mapping from a CSV file containing rows of |label, x, y|
    location_mapping = locationdictfromCSV(coordinatefile)
    # Get joblist dictionary from a JSON file
    joblist_dict = getjobDict(jobfile)
    
    # Initialize wallclock time - use a dummy date
    # Start simulation at midnight
    wallclock = datetime(2020,12,4,0,0,0,0)
    
    # Create a list of MSR robot objects 
    robot_list = [MSR(i,initloc_list[i-1],location_mapping,joblist_dict[str(i)]) for i in range(1,num_robots+1)]
    
    # Write header to output .csv file
    with open('/home/martijn/Simulations/MSR_state_simulation/output/main/{}'.format(outputfile), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Wallclock", "Robot", "State", "Duration", "From", "To", "TotalDistance", "IdleTime", "TotalTime"])

    # Simulate all robots
    Simulate(num_robots,robot_list,wallclock,outputfile) 
    
    # Make pie charts of the results
    createPlots(outputfile, num_robots)            
        