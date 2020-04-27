# speaker_level.py
import sys
import json
from os.path import exists

incoming_arguments = sys.argv[1]

speaker_info = json.loads(incoming_arguments)

print(incoming_arguments)
print(json.dumps(speaker_info))
