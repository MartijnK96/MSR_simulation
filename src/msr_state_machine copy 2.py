#!/usr/bin/python3

# rom transitions import Machine
import random
import time
from datetime import datetime, timedelta
from scipy.spatial import distance
#import pandas as pd
import csv
import operator
from collections import namedtuple


class MSR(object):

    def __init__(self, name, init_location, location_dictionary, job_list, start_times):
        self.name = name
        self.action = 'Park'
        self.duration = getSec(start_times[0])
        self.location_mapping = location_dictionary
        self.location = init_location
        self.speed = 2  # Speed in m/s

        # Distance traveled in meters
        self.distance_traveled = 0

        # Time active
        self.process_time = 0
        # Time idle (parking + waiting + charging)
        self.idle_time = 0

        # Battery charge is initially X hours or Y Ah -- research more how to handle this
        self.charge = 1000

        # Initialize list of jobs to execute
        self.job_list = job_list
        # Initialize a counter that counts the number of machines swabbed
        self.job_counter = 0
        
        

    def movetoLocation(self,task):
        global location_mapping
        self.action = 'Move'

        # Retrieve current location
        curr_loc = self.location_mapping(self.location)
        # Retrieve desired location
        des_loc = self.job_list[0][0][1]

        # Compute duration for movement
        moveto_duration = distance.euclidean(curr_loc, des_loc)/self.speed
        return moveto_duration
    
        # Handle some cases to determine duration from section to section etc.

    def waitforsectionPause(self):
        self.state = 'Wait'

        # Determine duration of waiting action - uniform distribution
        lbound_wait = 4
        hbound_wait = 10
        duration = random.uniform(lbound_wait, hbound_wait)
        return duration

    def Park(self, time):
        self.state = 'Park'

        park_duration = time
        return park_duration

    def chargeBattery(self):
        self.state = 'Charge'

        # Determine duration of charging - modify later
        charge_duration = 30*60
        return charge_duration

    def calibratetoSection(self):
        self.state = 'Calibrate'

        lbound_calibrate = 8
        hbound_calibrate = 12
        calibrate_duration = random.uniform(lbound_calibrate, hbound_calibrate)
        return calibrate_duration

    def Swab(self, sections=3):
        self.state = 'Swabbing'

        if sections == 3:  # If number of sections equals 3 the swabbing duration is 12s
            swab_duration = 12
        else:
            swab_duration = (2/3)*12

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


def locationdictfromCSV():
    f = open('coordinate_points.csv', 'r')
    reader = csv.reader(f)

    location_mapping = {}

    for row in reader:
        location_mapping[row[0]] = [float(x) for x in row[1:]]

    return location_mapping


if __name__ == '__main__':
    # Initialize wallclock time
    wallclock = 0

    # Assign an initial location to both robots
    initloc_msr1 = 'p1'
    initloc_msr2 = 'p2'

    location_mapping = locationdictfromCSV()
    
    subtasks_m1 = 

    # Specify jobs with starting times for both MSR1 and MSR2
    joblist_msr1 = [[('Move', 'm11'), ('Calibrate', 'm11'), ('Wait', 'm11'), ('Swab', 'm11')],
                    [('Move', 'm12'), ('Calibrate', 'm12'),
                     ('Wait', 'm12'), ('Swab', 'm12')],
                    [('Move', 'm13'), ('Calibrate', 'm13'),
                     ('Wait', 'm13'), ('Swab', 'm13')],
                    [('Move', 'm14'), ('Calibrate', 'm14'),
                     ('Wait', 'm14'), ('Swab', 'm14')],
                    [('Move', 'm15'), ('Calibrate', 'm15'),
                     ('Wait', 'm15'), ('Swab', 'm15')],
                    [('Move', 'm16'), ('Calibrate', 'm16'),
                     ('Wait', 'm16'), ('Swab', 'm16')],
                    [('Move', 'm17'), ('Calibrate', 'm17'),
                     ('Wait', 'm17'), ('Swab', 'm17')],
                    [('Move', 'm18'), ('Calibrate', 'm18'),
                     ('Wait', 'm18'), ('Swab', 'm18')],
                    ]

    msr1_starttimes = ['01:30:00', '03:00:00', '04:30:00',
                       '06:00:00', '07:30:00', '09:00:00', '10:30:00', '12:00:00']

    joblist_msr2 = [[('Move', 'm21'), ('Calibrate', 'm21'), ('Wait', 'm21'), ('Swab', 'm21')],
                    [('Move', 'm22'), ('Calibrate', 'm22'),
                     ('Wait', 'm22'), ('Swab', 'm22')],
                    [('Move', 'm23'), ('Calibrate', 'm23'),
                     ('Wait', 'm23'), ('Swab', 'm23')],
                    [('Move', 'm24'), ('Calibrate', 'm24'),
                     ('Wait', 'm24'), ('Swab', 'm24')],
                    [('Move', 'm25'), ('Calibrate', 'm25'),
                     ('Wait', 'm25'), ('Swab', 'm25')],
                    [('Move', 'm26'), ('Calibrate', 'm26'),
                     ('Wait', 'm26'), ('Swab', 'm26')],
                    [('Move', 'm27'), ('Calibrate', 'm27'),
                     ('Wait', 'm27'), ('Swab', 'm27')],
                    [('Move', 'm28'), ('Calibrate', 'm28'),
                     ('Wait', 'm28'), ('Swab', 'm28')],
                    ]

    msr2_starttimes = ['01:00:00', '03:00:00', '04:30:00',
                       '06:00:00', '07:30:00', '09:00:00', '10:30:00', '12:00:00']

    # Create i robot objects with different initial locations and jobs
    msr1 = MSR('msr1', initloc_msr1, location_mapping,
               joblist_msr1, msr1_starttimes)
    msr2 = MSR('msr2', initloc_msr2, location_mapping,
               joblist_msr2, msr2_starttimes)
    
    # Make list of robot objects
    robot_list = [msr1, msr2]

    while msr1.job_list or msr2.job_list:
        
        # Find robot with shortest remaining job duration, and the smallest remaining duration itself
        robot_list_sorted = sorted(robot_list, key=operator.attrgetter('duration'))
        smallest_duration = robot_list_sorted[0].duration
            
        for robot in robot_list:
            if robot.duration = smallest_duration
                # Execute task and remove task from joblist for this robot
                task = robot.joblist.pop(0) # Call robot transition function or make transition here - choice
                if task[0] == 'Move'
                    robot.movetoLocation()
            

    """ if msr1.process_time < msr2.process_time and msr1.job_list:
            # Do this
            print("MSR1's turn")
        elif msr1.process_time > msr2.process_time and msr2.job_list:
            # Do that
            print("MSR2's turn")
        else:
            # Do otherwise
            print("Pick one randomly")
            if random.choice([True, False]):
                print("MSR1's turn")
            else:
                print("MSR2's turn") """
