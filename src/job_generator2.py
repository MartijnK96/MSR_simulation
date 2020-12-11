#!/usr/bin/python3

import json
import sys
import datetime
import time
import argparse

class Machine(object):
    """
    Machine class idea.
    """
    def __init__(self, id, offset, interval):
        self.id = id
        self.time = offset[id]
        self.interval = interval

def parseArgs():
    parser = argparse.ArgumentParser(description='Generate joblists for MSR robots.')
    parser.add_argument('-r','--robots', type=int, default=2, help='Number of robots.')
    parser.add_argument('-m','--machines', type=int, default=4, help='Number of machines.')
    parser.add_argument('-s','--sections', type=int, default=8, help='Number of sections per machine.')
    parser.add_argument('-ma','--machineassign', type=int, nargs='+', action='append', help='Assigment of robots to machines.')
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
        key = 'msr' + str(robot) + '_joblist'
        lst = []
    
        assigned_machines = machine_dict[robot]
        print(assigned_machines)
        total_machines = list(range(1,machines+1))
        print(total_machines)
        swabtimes = swabtimes_dict.copy()
        
        for machine in filter(lambda machine: machine not in assigned_machines, total_machines):
            del swabtimes[machine]
            
        print(str(swabtimes))
        
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
        print(str(joblist_dict))
    
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
    
def sumTimestring(time1,time2):
    """
    Takes two time strings (hh:mm:ss) and sums them.

    Inputs:
        time1 (string): time string 1
        time2 (string): time string 2
    """
    (h1, m1, s1) = time1.split(':')
    d1 = datetime.timedelta(hours=int(h1), minutes=int(m1), seconds=int(s1))
    
    (h2, m2, s2) = time2.split(':')
    d2 = datetime.timedelta(hours=int(h2), minutes=int(m2), seconds=int(s2))
    
    return d1+d2
    
def sumStringTimedelta(timedelta, timestring):
    (h, m, s) = timestring.split(':')
    timedelta2 = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    
    return timedelta+timedelta2

def string2Timedelta(timestring):
    (h, m, s) = timestring.split(':')
    td = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    
    return td
    
def timestringtoSecs(ts):
    secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(ts.split(':'))))
    return secs

if __name__ == "__main__":
    # try:
    #     robots, machines, sections, intervals, offset, machines_robot = sys.argv
    # except IndexError:
    #     print("There appears to be an argument missing..")
    
    args = parseArgs()
    
    print(args)
    print(args.machineassign)
    print(type(args.swabinterval))
    
    # # Pass these ass command line arguments later on
    # robots = 2
    # machines = 4 
    # sections = 8
    # intervals = ['1:30:00','1:30:00','1:30:00','1:30:00']
    # offset = ['0:00:00','0:30:00','0:00:00','0:30:00']
    # # Stores machines that each MSR robot should service
    # machine_assign = {1: [1,2], 2: [3,4], 3: [], 4: []}
    
    # machine_list = creatmachineObj(machines,intervals,offset)
    
    # job_dict = jobGenerator(machines, sections)
    
    # swabtimes_dict = generateswabTimes(machines,intervals,offset)
    
    # print(str(swabtimes_dict))
    
    # #time.sleep(20)
    
    # joblist_dict = joblistGenerator(robots, job_dict, machines, machine_assign, swabtimes_dict)
    
    # with open('job_list.json', 'w') as f:
    #     f.write(json.dumps(joblist_dict['msr1_joblist']))
    #     f.write(json.dumps(joblist_dict['msr2_joblist']))
        
    
    
    

    
    