# If then and groups prototype
from sys import exit
import os, fnmatch
import requests
import json
import re

path_to_files = './groups/'
base_url = "http://192.168.0.101:3689"
filename = "group_name.json"
avialable_outputs = {}


def search(search_where, search_for, search_field, return_what):
    i = 0
    match = False
    for thing in search_where:
        test = search_where[i][search_field].lower()
        if test == search_for.lower():
            match = True
            returned = search_where[i][return_what]
        i += 1
    if match:
        return(returned)
    else:
        return(-1)

# get available outputs from forked-daapd
def get_outputs():
    outputs = requests.get(base_url + '/api/outputs').json()
    outputs = outputs.get('outputs')
    i = 0
    for output in outputs:
            avialable_outputs[i] = output
            i += 1
    return avialable_outputs

# get existing groups from .groups file
def get_groups():
    global existing_groups
    existing_groups = []
    group_files = open(path_to_files + '.groups', "r")
    i = 0
    for entry in group_files:
        existing_groups.append(entry.strip('\n'))
        i += 1
    group_files.close()
    return existing_groups

# read the JSON file containing group info
def read_group_file(group_name):
    global current_group
    current_group = {}
    group_file = f"{path_to_files}{group_name}.json"
    group = open(group_file).read()
    group = json.loads(group)
    current_group = group[group_name]
    return current_group

# write the .group file containing names of groups
def write_group_file():
    filename = path_to_files + '.groups'
    target = open(filename, 'w')
    for entry in existing_groups:
        target.write(entry+'\n')
    target.close()

# make a new group
def create_group(group_name, group_items, mode):
    get_groups()
    json_output = {}
    temp_items = []
    add_conf = ''
    json_output[group_name] = {}
    get_outputs()
    for item in group_items:
        temp_items.append(
            dict(id=search(avialable_outputs, item['name'], "name", "id"),
            name = item['name'], volume = str(item['volume']),
            selected = True)
        )
    json_output[group_name] = temp_items
    existing_groups.append(group_name)
    existing_groups.sort()

    filename = path_to_files + group_name + '.json'
    target = open(filename, 'w')
    target.truncate()
    target.write(json.dumps(json_output, indent=4))
    target.close()
    if mode == "new":
        write_group_file()
    return True

# delete an existing group 
def delete_group(group_name):
    get_groups()
    if group_name in existing_groups:
        item_index = existing_groups.index(group_name)
    file_to_del = path_to_files + existing_groups[item_index]+'.json'
    if os.path.exists(file_to_del):
        os.remove(file_to_del)
    else:
        print(f"File {file_to_del} dosn't exist")
        return False

    del existing_groups[item_index]
    existing_groups.sort()
    write_group_file()
    return True
