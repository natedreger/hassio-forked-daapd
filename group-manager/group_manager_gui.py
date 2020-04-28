#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import group_manager_modules


window = tk.Tk()

# Global Variables
output_str = ""
group_str = ""
speaker_checkboxes = {}
speaker_sliders = {}
available_groups = []
available_outputs = {}

class speaker_handle(object):
    def __init__(self, name):
        checkbutton = ttk.Checkbutton(master=frm_create, text = self.name)
        slider = tk.Scale(master = frm_create, from_=0, to=100, orient=tk.HORIZONTAL)

def handle_keypress(event):
    #ctrl-q to quit
    if event.char == "\x11":
        window.destroy()
    else:
        pass

def refresh_speakers():
    global available_outputs
    i = 0
    output_str = ""
    available_outputs = group_manager_modules.get_outputs()
    for output in available_outputs:
        output_str += available_outputs[i]['name'] + '\n'
        i += 1
    lbl_speakers["text"] = f"Available Speakers\n\n{output_str}"

def refresh_groups():
    global group_str
    group_str = ""
    available_groups = group_manager_modules.get_groups()
    for group in available_groups:
        group_str += group + '\n'
    lbl_groups["text"] = f"Current Groups\n\n{group_str}"

# build the checkboxes and volume sliders for available speakers and set defaults based on view mode
def build_speaker_checks(dict, frame, mode):
    i = 0
    tmp_dict = {}
    dict_b = dict
    dict = available_outputs
    for speaker in dict:
        # make checkbuttons
        speaker_checkboxes[dict[i]['name']] = ttk.Checkbutton(master = frame, text = dict[i]['name'])
        speaker_checkboxes[dict[i]['name']].grid(row=i, column = 0, pady = 20, padx = 10, sticky = "sw")
        # clear checkbuttons
        speaker_checkboxes[dict[i]['name']].state(['!alternate'])
        speaker_checkboxes[dict[i]['name']].state(['!selected'])
        # make volume sliders
        speaker_sliders[dict[i]['name']] = tk.Scale(master = frame, from_=0, to=100, orient=tk.HORIZONTAL)
        speaker_sliders[dict[i]['name']].grid(row=i, column = 1, sticky = "w")

        if mode == "view":
            speaker_checkboxes[dict[i]['name']].state(['!alternate'])
            speaker_checkboxes[dict[i]['name']].state(['!selected'])
            speaker_sliders[dict[i]['name']].set(dict[i]['volume'])
            if dict[i]['selected']:
                speaker_checkboxes[dict[i]['name']].state(['alternate'])
        elif mode == "create":
            speaker_checkboxes[dict[i]['name']].state(['!alternate'])
            speaker_checkboxes[dict[i]['name']].state(['!selected'])
            speaker_sliders[dict[i]['name']].set(50)
        elif mode == "edit":
            for item in dict_b:
                if item['name'] == dict[i]['name']:
                    speaker_checkboxes[dict[i]['name']].state(['!alternate'])
                    speaker_checkboxes[dict[i]['name']].state(['selected'])
                    speaker_sliders[dict[i]['name']].set(item['volume'])
        elif mode == "clear":
                speaker_checkboxes[dict[i]['name']].state(['!alternate'])
                speaker_checkboxes[dict[i]['name']].state(['!selected'])
        i += 1

# create mode
def create(group_name, mode):
    if mode == "new" and group_name.lower() in group_str.lower():
        ent_group_name.delete(0, tk.END)
        ent_group_name.insert(0, f"Enter Unique Name")
    else:
        if group_name:
            group_items = []
            for box in speaker_checkboxes:
                box_val = speaker_checkboxes[box].state()
                if "selected" in box_val:
                    volume = speaker_sliders[box].get()
                    group_items.append(dict(name = box, volume = volume))
                #    print(f"{box} added at {volume}%")
                else:
                    selected = False
                speaker_checkboxes[box].state(['!selected'])
            if len(group_items) > 0:
                if group_manager_modules.create_group(group_name, group_items, mode):
                    ent_group_name.delete(0, tk.END)
                    ent_group_name.insert(0, f"{group_name} Group Created")
                    refresh_groups()
                    com_group_name['values'] = group_str
                    com_group_name.set("")
                else:
                    ent_group_name.delete(0, tk.END)
                    ent_group_name.insert(0, f"Failed to Create {group_name}")
            else:
                ent_group_name.delete(0, tk.END)
                ent_group_name.insert(0, f"Nothing Selected")

# edit mode
def edit(group_name):
    # read the group file
    group_manager_modules.read_group_file(group_name)
    # check boxes and set volumes
    build_speaker_checks(group_manager_modules.current_group, frm_edit, "edit")
    # saving done using create function

def del_group(group_name):
    '''
    pop up confirmation window
    if yes then call delete function from
    '''
    if group_manager_modules.delete_group(group_name):
        refresh_groups()
        com_group_name['values'] = group_str
        com_group_name.set("")
        print("SUCCESS")
    else:
        # pop up something failed
        pass

def create_page():
    # place create page in frm_center
    build_speaker_checks(available_outputs, frm_create, "clear")
    build_speaker_checks(available_outputs, frm_create, "create")
    ent_group_name.delete(0, tk.END)
    frm_create.tkraise()
    pass

def edit_page():
    build_speaker_checks(available_outputs, frm_edit, "clear")
    frm_edit.tkraise()
    # place edit page in frm_center
    pass

def home_page():
    build_speaker_checks(available_outputs, frm_create, "clear")
    build_speaker_checks(available_outputs, frm_center, "view")
    frm_center.tkraise()


# Define Window layout
window.title("Group Manager")
window.geometry('600x500')
window.minsize(600,500)
window.rowconfigure(0, minsize = 700, weight = 1)
window.columnconfigure([0,2], minsize = 150, weight = 1)
window.columnconfigure(1, minsize = 250, weight = 1)

# Define Frames
frm_left = tk.Frame(master = window)
frm_center = tk.Frame(master = window)
frm_create = tk.Frame(master = window)
frm_edit = tk.Frame(master = window)
frm_right = tk.Frame(master = window)
frm_right.rowconfigure([1,2,3,4], minsize = 100)

# Widgets
btn_home = tk.Button(master = frm_left, width = 8, text = "Home", command = home_page)
btn_create_page = tk.Button(master = frm_left, text="Create", width = 8, command = create_page)
btn_edit_page = tk.Button(master = frm_left, text="Edit", width = 8, command = edit_page)
btn_edit = tk.Button(master = frm_edit, text="Edit", width = 8, command = lambda: edit(com_group_name.get()))
btn_save_edit = tk.Button(master = frm_edit, text="Save", width = 8, command = lambda: create(com_group_name.get(), "edit"))
btn_speaker_refresh = tk.Button(master = frm_right, text="Refresh", command = lambda: refresh_speakers())
btn_group_refesh = tk.Button(master = frm_right, text = "Refresh", command =  refresh_groups)
btn_make_group = tk.Button(master = frm_create, text = "Make It!", command = lambda: create(ent_group_name.get(), "new"))
btn_del_grp = tk.Button(master = frm_edit, text="Delete", width = 8, command = lambda: del_group(com_group_name.get()))
btn_quit = tk.Button(master = frm_left, width = 8, text = "Quit", command = lambda: window.destroy())

lbl_group_name = tk.Label(master = frm_create, text = "Enter name for group:")
lbl_speakers = tk.Label(master = frm_right, text="Available Speakers\n\nNo Speakers Available", width = 20)
lbl_groups = tk.Label(master = frm_right, text = "Current Groups\n\nNo Groups Found", width = 20)
lbl_choose_grp = tk.Label(master = frm_edit, text = "Choose a Group")

ent_group_name = tk.Entry(master = frm_create, text = "")


# need to get some info before we move on
refresh_groups()
refresh_speakers()
build_speaker_checks(available_outputs, frm_center, "view")
com_group_name = ttk.Combobox(frm_edit, width = 15, values = group_str)

# Build GUI
# Left frame
btn_home.grid(row = 0, padx = 5, pady = 5, sticky = "ns")
btn_create_page.grid(row = 1, padx = 5, pady = 5, sticky = "ns")
btn_edit_page.grid(row = 2, padx = 5, pady = 5, sticky = "ns")
btn_quit.grid(row = 3, padx = 5, pady = 20, sticky = "ns")

# Right frame
lbl_speakers.grid(row = 0, padx = 5, pady = 5, sticky = "n")
btn_speaker_refresh.grid(row = 1, sticky = "n")
lbl_groups.grid(row = 2, padx = 5, pady = 5, sticky = "s")
btn_group_refesh.grid(row = 3, sticky = "n")

# "Create Frame"
lbl_group_name.grid(row = len(speaker_checkboxes)+10, column = 0, columnspan = 2)
ent_group_name.grid(row = len(speaker_checkboxes)+11, column = 0, columnspan = 2)
btn_make_group.grid(row = len(speaker_checkboxes)+12, column = 0, columnspan = 2, pady = 10)

# Edit Frame
lbl_choose_grp.grid(row = len(speaker_checkboxes)+10, column = 0, sticky = "s")
com_group_name.grid(row = len(speaker_checkboxes)+11, column = 0, padx = 5, sticky = "n")
btn_edit.grid(row = len(speaker_checkboxes)+10, column = 1, pady = 5, sticky = "n")
btn_save_edit.grid(row = len(speaker_checkboxes)+11, column = 1, pady = 5, sticky = "n")
btn_del_grp.grid(row = len(speaker_checkboxes)+12, column = 1, pady = 5, sticky = "n")

# Window
frm_left.grid(row = 0, column = 0, sticky = "wns")
frm_center.grid(row = 0, column = 1, sticky = "news")
frm_edit.grid(row = 0, column = 1, sticky = "wens")
frm_create.grid(row = 0, column = 1, sticky = "wens")
frm_right.grid(row = 0, column = 2, sticky = "nse")
###
home_page()
window.bind("<Key>", handle_keypress)
window.mainloop()
