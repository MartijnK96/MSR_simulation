#!/usr/bin/python3

import json
import sys
import datetime
import time
import argparse
import os
from os.path import dirname as dir

class Machine(object):
    """
    Machine class idea.
    """
    def __init__(self, id, offset, interval):
        self.id = id
        self.time = offset[id]
        self.interval = interval

def parseArgs():
    """
    Argument parser function.

    Returns:
        args (argument list): input arguments
    """
    
    parser = argparse.ArgumentParser(description='Generate joblists for MSR robots.')
    parser.add_argument('-f','--filename',type=str, default='job_list.json', help='Name of the JSON file to write to.')
    parser.add_argument('-r','--robots', type=int, default=2, help='Number of robots.')
    parser.add_argument('-m','--machines', type=int, default=4, help='Number of machines.')
    parser.add_argument('-s','--sections', type=int, default=8, help='Number of sections per machine.')
    parser.add_argument('-ma','--machineassign', type=int, nargs='+', action='append', default= [[1,2], [3,4]], help='Assigment of robots to machines.')
    parser.add_argument('-int','--swabinterval', nargs="+", default=['1:30:00','1:30:00','1:30:00','1:30:00'], help='Swabbing interval for each machine.')
    parser.add_argument('-off','--swaboffset', nargs="+", default=['0:00:00','0:30:00','0:00:00','0:30:00'], help='Offset for each machine w.r.t. midnight.')
    
    args = parser.parse_args()
    
    return args

def jobGenerator(machines,sections):
    """
    Returns a dictionary with jobs for each machine
    
    Inputs: 
        machines (int): number of machines
        sections (int): number of sections
    Output: 
        job_dict (dict): dictionary with jobs for each machine (keys: 'm1_job', .., 'mn_job')
    """
    job_dict = {}
    for machine in range(1,machines+1):
        key = machine
        lst = []
        
        for section in range(1,sections+1):
            lst.append(('Move','m'+str(machine)+str(section)))
            lst.append(('Calibrate','m'+str(machine)+str(section)))
            lst.append(('Wait','m'+str(machine)+str(section)))
            lst.append(('Swab','m'+str(machine)+str(section)))
            
        job_dict[key] = lst
        
    return job_dict

def joblistGenerator(robots, job_dict, machines, machine_dict, swabtimes_dict):
    """
    Returns a dictionary containing job lists for all MSR robots.

    Inputs:
        robots (int): number of MSR robots
        intervals (list(string)): list with swabbing intervals for each machine
        offset (string): time offset for first swabbing job from midnight ('00:00:00')
        job_dict (dict): job dictionary containing swabbing job subtasks for each machine (job_dict[i] gives the subtasks for swabbing mi)
    """
    
    joblist_dict = {}
    for robot in range(1,robots+1):
        key = robot
        lst = []
    
        assigned_machines = machine_dict[robot]
        total_machines = list(range(1,machines+1))
        swabtimes = swabtimes_dict.copy()
        
        for machine in filter(lambda machine: machine not in assigned_machines, total_machines):
            del swabtimes[machine]
            
        done = len(swabtimes)
        num_empty = 0 
        while (num_empty < done):
            min_key = min(swabtimes,key=lambda key:min(swabtimes[key]))
            time = swabtimes[min_key].pop(0)
            
            lst.append([('Park',time)])
            lst.append(job_dict[min_key][:])
            
            for machine in list(swabtimes.keys()): 
                if not swabtimes[machine]:
                    num_empty += 1
                    del swabtimes[machine]

        joblist_dict[key] = lst
    
    return joblist_dict
                    
def creatmachineObj(machines,intervals,offset):
    """
    Returns a list of machine objects.

    Inputs:
        machines (int): number of IS machines
        intervals (list(string)): list with swabbing intervals for each machine
        offset (list(string)): time offset for first swabbing job from midnight ('00:00:00')
    Outputs:
        machine_list (list(obj)): list of machine objects
    """
    machine_list = []
    for machine in range(0,machines):
        id = machine+1
        machine_list.append(Machine(id,offset[machine],intervals[machine]))
                            
    return machine_list

def generateMAdict(list):
    """
    Returns dictionary with machine assignment for robots.
    """
    
    machineassign_dict = {}
    for i in range(len(list)):
        key = i+1 
        machineassign_dict[key] = list[i]
    
    return machineassign_dict
    
def generateswabTimes(machines,intervals,offset):
    """
    Generates a dictionary containing lists of swabbing times for each IS machine.
    
    Inputs:
        machines (int): number of IS machines
        intervals (list(string)): list with swabbing intervals for each machine 
        offset (list(string)): 
    """
    swabtimes_dict = {}
    midnight = datetime.timedelta(hours=24,minutes=0,seconds=0)
    for machine in range(1,machines+1):
        # Machine goes from 1,..,4; lists are indexed at 0
        key = machine
        
        clocktime = string2Timedelta(offset[machine-1])
        interval = string2Timedelta(intervals[machine-1])
        
        lst = []
        lst.append(offset[machine-1])
        while (clocktime + interval < midnight):
            lst.append(str(clocktime+interval))
            
            clocktime += interval
            
        swabtimes_dict[key] = lst
        
    return swabtimes_dict

def string2Timedelta(timestring):
    (h, m, s) = timestring.split(':')
    td = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    
    return td

if __name__ == "__main__":
    
    args = parseArgs()
    
    filename = args.filename
    robots = args.robots
    machines = args.machines
    sections = args.sections
    intervals = args.swabinterval
    offset = args.swaboffset
    machineassign = args.machineassign
    
    # Generate dictionary of machine assignment list
    machine_assign = generateMAdict(machineassign)
    
    # Generate dictionary of jobs for each machine
    job_dict = jobGenerator(machines, sections)
    
    # Generate dictionary with swabbing times for each machine
    swabtimes_dict = generateswabTimes(machines,intervals,offset)

    # Generate dictionary with joblists for each MSR
    joblist_dict = joblistGenerator(robots, job_dict, machines, machine_assign, swabtimes_dict)
    
    # Write joblists to JSON file with filename specified in command line
    project_dir = dir(dir((__file__)))
    relative_path =  'input/joblist/{}'.format(filename)
    file_path = os.path.join(project_dir, relative_path)
    with open(file_path, 'w') as f:
        json.dump(joblist_dict,f,indent=1)