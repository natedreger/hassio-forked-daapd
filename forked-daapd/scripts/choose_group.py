import sys
import json
from os.path import exists
import requests

outputs_file = "/config/forked-daapd/groups/AllOutputs.json"
groups_file = "/config/forked-daapd/groups/EverywhereNew.json"
to_file = "/config/forked-daapd/groups/testout.txt"

group_name = sys.argv[1]

outputs = open(outputs_file).read()
outputs = json.loads(outputs)

group = open(groups_file).read()
group = json.loads(group)

#print(outputs['outputs'][0]['name'])
#print(outputs['outputs'][0]['id'])
#print("Items in Group")
#print(group_name)
i = 0
for speaker in group[group_name]:
#    print(group[group_name][i]['id'])
    i += 1

group_json = json.dumps(group)
print(group_json)
