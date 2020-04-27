import appdaemon.plugins.hass.hassapi as hass
from os.path import exists
import requests
import json
import sys

path_to_group_file = "/config/forked-daapd/groups/"
base_url = "http://192.168.0.101:3689"     # you're forked-daapd ip

# prefix and suffix so we can tell hassio what to control later

spkr_switch_prfx = "input_boolean."        # could be a switch if prefered
spkr_switch_sffx = "_speaker"              # example input_boolean.office_speaker
spkr_lvl_prfx = "input_number."
spkr_lvl_sffx = "_speaker_level"           # example input_number.office_speaker
# build empty dicts to fill later
outputs = {}
current_group = {}

# appdaemon classes for hassio
class ForkedDaapedControl(hass.Hass):

    def initialize(self):
        self.log("ForkedDaapedControl is running")
        global hassio
        hassio = self
        # tell appdaemon what to listen for to control groups and individual speakers
        self.listen_state(set_group,"input_select.speaker_group")
        self.listen_state(speaker_toggle, "input_boolean")
        self.listen_state(speaker_toggle, "sensor.multipi_office", attribute = "all")
        self.listen_state(speaker_toggle, "sensor.multipi_iphone",  attribute = "all")
        self.listen_state(speaker_toggle, "sensor.multipi_livingroom",  attribute = "all")
        self.listen_state(speaker_toggle, "sensor.multipi_bedroom", attribute = "all")

class ForkedDaapedPlaylist(hass.Hass):

    def initialize(self):
        # listen for change of playlist
        self.listen_state(set_playlist, "input_select.multipi_source")

############################################################################################

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
# Function to get available playlists from forked-daapd
def get_playlists():
    global available_playlists
    playlists = requests.get(base_url+'/api/library/playlists').json()
    available_playlists = playlists.get('items')

# Function to play new playlist in forked-daapd
def set_playlist(entity, attribute, old, new, kwargs):
    print(f"Playlist changed from {old} to {new}")
    # get playlists
    get_playlists()
    # get search playlists for new and get the id number
    new_playlist = search(available_playlists, new, 'name', 'id')
    playlist_url = base_url + '/api/queue/items/add?uris=library:playlist:' + str(new_playlist)
    requests.put(base_url + '/api/queue/clear')
    playlist_response = requests.post(playlist_url)
    print(playlist_response)
    if playlist_response.status_code == 204:
        print(f"Success, added {new} id:{new_playlist} to queue")
    else:
        print(f"Something went wrong add adding {new} to queue")
    requests.put(base_url+'/api/player/play')

# Function to get available outputs from forked-daapd
def get_outputs():
    global available_outputs
    outputs = requests.get(base_url+'/api/outputs').json()
    available_outputs = outputs.get('outputs')

# set group speakers on, off, volume according to JSON
def set_group_speakers(group, group_name, avialable_outputs):
    # loop through group and turn things on
    for speaker in group:
        # search available_outputs for speaker name and get correct id
        id = search(avialable_outputs, speaker['name'], 'name', 'id')
        if id != -1:
            # turn speakers on
            on_data = '{\"selected\":true}'
            on_url = base_url + '/api/outputs/' + id
            on_response = requests.put(on_url, data=on_data)
            if on_response.status_code == 204:
                print(f"{speaker['name']} turned on")
                # turn on input_boolean for speaker
                hassio.turn_on(f"{spkr_switch_prfx}{speaker['name'].lower()}{spkr_switch_sffx}")
            else:
                print("Something went wrong with", speaker['name'])
            # set speaker volumes
            vol_url = base_url + '/api/player/volume?volume=' + speaker['volume'] + '&output_id=' + id
            vol_response = requests.put(vol_url)
            if vol_response.status_code == 204:
                print (f"Volume for {speaker['name']} set to {speaker['volume']}")
                hassio.set_value(f"{spkr_lvl_prfx}{speaker['name'].lower()}{spkr_lvl_sffx}", speaker['volume'])
            else:
                print(f"Somthing went wrong setting volume for {speaker['name']}")
        elif id == -1:
            print(speaker['name'], "not available")

    # loop through the outputs and turn off whats not in group
    for output in available_outputs:
        id = search(group, output['name'], 'name', 'id')
        if id == -1:
            data = '{\"selected\":false}'
            url = base_url + '/api/outputs/' + output['id']
            response = requests.put(url, data=data)
            if response.status_code == 204:
                print(f"{output['name']} turned off")
                # turn off input_boolean for speaker
                hassio.turn_off(f"{spkr_switch_prfx}{output['name'].lower()}{spkr_switch_sffx}")
            else:
                print("Something went wrong with", output['name'])

def all_off():
    for output in available_outputs:
        data = '{\"selected\":false}'
        url = base_url + '/api/outputs/' + output['id']
        response = requests.put(url, data=data)
        if response.status_code == 204:
            print(f"{output['name']} turned off")
            # turn off input_boolean for speaker
            hassio.turn_off(f"{spkr_switch_prfx}{output['name'].lower()}{spkr_switch_sffx}")
        else:
            print("Something went wrong with", output['name'])

# get group name and build the dict from file
def set_group(entity, attribute, old, new, kwargs):
    group_name = new
    global current_group
    get_outputs()
    #global available_outputs

    #outputs = requests.get(base_url+'/api/outputs').json()
    #available_outputs = outputs.get('outputs')

    if group_name != "None":
        group_file = f"{path_to_group_file}{group_name}.json"
        group = open(group_file).read()
        group = json.loads(group)
        current_group = group[group_name]
        set_group_speakers(current_group, group_name, available_outputs)
    else:
        all_off()

# input boolean controls, manual and sensor triggered
def speaker_toggle(entity, attribute, old, new, kwargs):
    get_outputs()
    domain, entity = hassio.split_entity(entity)
    # manual triggering
    if domain == "input_boolean":
        speaker = entity.split('_')
        speaker = speaker[0]
        speaker_id = search(available_outputs, speaker, 'name', 'id')
        selected = hassio.get_state(f"sensor.multipi_{speaker}", attribute = "selected")
        if selected != None:
            available = True
        else:
            available = False
        if domain == "input_boolean" and entity.find(spkr_switch_sffx) != -1 and available == True:
            if new == "on":
                new = 'true'
            else:
                new = 'false'
            toggle_data = '{\"selected\":' + new + '}'
            toggle_url = base_url + '/api/outputs/' + speaker_id
            toggle_response = requests.put(toggle_url, data=toggle_data)
            if toggle_response.status_code == 204:
                print(f"{speaker} turned {new}")
            else:
                print("Something went wrong with", speaker)
        elif available != True:
            hassio.turn_off(f"{spkr_switch_prfx}{speaker}{spkr_switch_sffx}")

    # set input_boolean based on sensor value
    if domain == "sensor":
        speaker = entity.split('_')
        speaker = speaker[1]
        selected = hassio.get_state(f"sensor.multipi_{speaker}", attribute = "selected")
        if selected != None:
            available = True
        else:
            available = False
        if available == True and selected == True:
            hassio.turn_on(f"{spkr_switch_prfx}{speaker}{spkr_switch_sffx}")
        else:
            hassio.turn_off(f"{spkr_switch_prfx}{speaker}{spkr_switch_sffx}")

##############################################################################################
