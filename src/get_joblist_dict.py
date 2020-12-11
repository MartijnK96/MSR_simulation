#!/usr/bin/python3

import json

with open('experiment001.json', 'r') as fjson:
        joblist_dict = json.load(fjson)
        
for joblist in joblist_dict:
    for idx, job in enumerate(joblist_dict[joblist]):
        joblist_dict[joblist][idx] = [tuple(subtask) for subtask in job]
        
print(joblist_dict)
            
print(joblist_dict['msr1_joblist'][1])