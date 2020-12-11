#!/usr/bin/python3

import json 

with open('experiment001.json', 'r') as fjson:
    joblist_data = json.load(fjson)
    
print(joblist_data['msr1_joblist'])

print(len(joblist_data))