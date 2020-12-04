#!/usr/bin/python3

# from transitions import Machine
import random
import time
from datetime import time, date, datetime, timedelta
from scipy.spatial import distance
#import pandas as pd
import csv
import operator
from collections import namedtuple


class MSR(object):

    def __init__(self, id, init_location, location_dictionary, job_list, start_times):
        self.ID = id
        self.state = 'Park'
        # TODO: Obtain duration differently
        self.duration = getSec(msr1_joblist[0][0][1])
        self.location_mapping = location_dictionary
        self.location = init_location
        self.speed = 2  # Speed in m/s

        # Distance traveled in meters
        self.distance_traveled = 0

        # Time active - not used currently
        self.robotclock = 0 
        # Time idle (parking + waiting + charging)
        self.idle_time = 0

        # Battery charge is initially X hours or Y Ah -- research more how to handle this
        self.charge = 1000

        # Initialize list of jobs to execute
        self.job_list = job_list
        # Initialize a counter that counts the number of machines swabbed
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
            duration = self.Park()
        elif task_name = 'Charge':
            duration = self.chargeBattery()
        elif task_name = 'Calibrate':
            duration = self.calibratetoSection()
        elif task_name = 'Swab':
            try:
                sections = task[2]
                duration = self.Swab(sections)
            except IndexError:
                duration = self.Swab()
                     
            duration = self.Swab(sections)
            
        print(wallclock.strftime("%H:%M:%S") + ": MSR" + str(self.ID) + " performed state " + task_name + 
              " at " + self.location + " with duration " + str(self.duration) + " seconds.")
            
    # TODO: Function should execute resursively if moving from a charging point - c1 - to a machine section - m11 - for instance
    def movetoLocation(self,task):
        global location_mapping
        self.state = 'Move'

        # Retrieve current location
        curr_loc = self.location_mapping(self.location)
        # Retrieve desired location
        des_loc = self.job_list[0][0][1]

        # Compute duration for movement
        moveto_duration = distance.euclidean(curr_loc, des_loc)/self.speed
        self.duration = moveto_duration
        self.robotclock += moveto_duration
        
        return moveto_duration
    
        # Handle some cases to determine duration from section to section etc.

    def waitforsectionPause(self):
        self.state = 'Wait'

        # Determine duration of waiting action - uniform distribution
        lbound_wait = 4
        hbound_wait = 10
        wait_duration = random.uniform(lbound_wait, hbound_wait)
        self.duration = wait_duration
        self.robotclock += wait_duration
        
        return wait_duration

    def Park(self, task):
        self.state = 'Park'

        park_duration = getSec(task[2]) - self.robotclock
        self.idle_time += park_duration 
        self.duration = park.duration
        self.robotclock += park_duration
        
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
            swab_duration = random.normal(mean_3sec,0.1,1)
        else:
            mean = (sections/3)*mean_3sec
            swab_duration = random.normal(mean,0.1,1)
            
        self.duration = swab_duration
        self.robot_clock += swab_duration

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
    # Initialize wallclock time - use a dummy date
    # Start simulation at midnight
    wallclock = datetime(2020,12,4,0,0,0,0)

    # Assign an initial location to both robots
    initloc_msr1 = 'p1'
    initloc_msr2 = 'p2'

    location_mapping = locationdictfromCSV()
    
    # Define subtasks of a swabbing job
    # TODO: Create job/task-generator function
    #machines = 4
    #for machine in machines:
    m1_job = [('Move','m11'),('Calibrate','m11'),('Wait','m11'),('Swab','m11'),
              ('Move','m12'),('Calibrate','m12'),('Wait','m12'),('Swab','m12'),
              ('Move','m13'),('Calibrate','m13'),('Wait','m13'),('Swab','m13'),
              ('Move','m14'),('Calibrate','m14'),('Wait','m14'),('Swab','m14'),
              ('Move','m15'),('Calibrate','m15'),('Wait','m15'),('Swab','m15'),
              ('Move','m16'),('Calibrate','m16'),('Wait','m16'),('Swab','m16'),
              ('Move','m17'),('Calibrate','m17'),('Wait','m17'),('Swab','m17'),
              ('Move','m18'),('Calibrate','m18'),('Wait','m18'),('Swab','m18')]
    
    m2_job = [('Move','m21'),('Calibrate','m21'),('Wait','m21'),('Swab','m21'),
              ('Move','m22'),('Calibrate','m22'),('Wait','m22'),('Swab','m22'),
              ('Move','m23'),('Calibrate','m23'),('Wait','m23'),('Swab','m23'),
              ('Move','m24'),('Calibrate','m24'),('Wait','m24'),('Swab','m24'),
              ('Move','m25'),('Calibrate','m25'),('Wait','m25'),('Swab','m25'),
              ('Move','m26'),('Calibrate','m26'),('Wait','m26'),('Swab','m26'),
              ('Move','m27'),('Calibrate','m27'),('Wait','m27'),('Swab','m27'),
              ('Move','m28'),('Calibrate','m28'),('Wait','m28'),('Swab','m28')]
    
    m3_job = [('Move','m31'),('Calibrate','m31'),('Wait','m31'),('Swab','m31'),
              ('Move','m32'),('Calibrate','m32'),('Wait','m32'),('Swab','m32'),
              ('Move','m33'),('Calibrate','m33'),('Wait','m33'),('Swab','m33'),
              ('Move','m34'),('Calibrate','m34'),('Wait','m34'),('Swab','m34'),
              ('Move','m35'),('Calibrate','m35'),('Wait','m35'),('Swab','m35'),
              ('Move','m36'),('Calibrate','m36'),('Wait','m36'),('Swab','m36'),
              ('Move','m37'),('Calibrate','m37'),('Wait','m37'),('Swab','m37'),
              ('Move','m38'),('Calibrate','m38'),('Wait','m38'),('Swab','m38')]
    
    m4_job = [('Move','m41'),('Calibrate','m41'),('Wait','m41'),('Swab','m41'),
              ('Move','m42'),('Calibrate','m42'),('Wait','m42'),('Swab','m42'),
              ('Move','m43'),('Calibrate','m43'),('Wait','m43'),('Swab','m43'),
              ('Move','m44'),('Calibrate','m44'),('Wait','m44'),('Swab','m44'),
              ('Move','m45'),('Calibrate','m45'),('Wait','m45'),('Swab','m45'),
              ('Move','m46'),('Calibrate','m46'),('Wait','m46'),('Swab','m46'),
              ('Move','m47'),('Calibrate','m47'),('Wait','m47'),('Swab','m47'),
              ('Move','m48'),('Calibrate','m48'),('Wait','m48'),('Swab','m48')]

    # Specify jobs for both MSR1 and MSR2
    # TODO: Specify parking end-times
    msr1_joblist = [[('Park','01:30:00')],m1_job,[('Park','03:00:00')],m1_job,[('Park','04:30:00')],m1_job,[('Park','06:00:00')],m1_job,[('Park','07:30:00')]
                    ,m1_job,[('Park','09:00:00')],m1_job,[('Park','10:30:00')],m1_job,[('Park','12:00:00')],m1_job,[('Park','13:30:00')]]
    
    msr2_joblist = [m2_job,[('Park','01:00:00')],m2_job,[('Park','02:00:00')],m2_job,[('Park','03:00:00')],m2_job,[('Park','04:00:00')]
                    ,m2_job,[('Park','05:00:00')],m2_job,[('Park','06:00:00')],m2_job,[('Park','07:00:00')],m2_job,[('Park','08:00:00')]]

    # Create i robot objects with different initial locations and jobs
    msr1 = MSR(1, initloc_msr1, location_mapping, msr1_joblist)
    msr2 = MSR(2, initloc_msr2, location_mapping, msr2_joblist)
    
    # Make list of robot objects
    robot_list = [msr1, msr2]

    while msr1.job_list or msr2.job_list:
        
        # Find robot with shortest remaining job duration, and the smallest remaining duration itself
        robot_list_sorted = sorted(robot_list, key=operator.attrgetter('duration'))
        smallest_duration = robot_list_sorted[0].duration
        
        wallclock += timedelta(seconds=smallest_duration)
            
        for robot in robot_list:
            if robot.duration == smallest_duration:
                # Execute task and remove task from joblist for this robot
                # Check size of list and remove from joblist if empty
                if not robot.joblist[0]:
                    # Delete the empty job
                    del robot.joblist[0]
                    
                    # And pop the task from the next job
                    task = robot.joblist[0].pop(0)
                    robot.transFunc(task,wallclock)
                else:
                    task = robot.joblist[0].pop(0) # Call robot transition function or make transition here - choice
                    robot.transFunc(task,wallclock)
            else: 
                robot.duration -= smallest duration