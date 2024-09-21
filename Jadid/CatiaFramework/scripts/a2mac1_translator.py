"""
This is a translator of html page specifically
developed for a2mac1 component tree.
Usage: simply run code, select a file with
    conform structure and a result/output file
    will be automatically saved as JSON with
    name of the preselected file.
"""
from tkinter import filedialog as fd
import json

ins = fd.askopenfile()
file_to_read = open(ins.name, "r")
parsed_string = file_to_read.read()
parsed_string = parsed_string.replace("ng-star-inserted", "")
parsed_string = parsed_string.replace("_ngcontent-cbs-c228=""", "")
parsed_string = parsed_string.replace("<!---->", "")
start_id, end_id = 1, 1
while not (start_id == -1 or end_id == -1):
    start_id, end_id = parsed_string.find("<button"), parsed_string.find("</button>")
    if end_id > start_id:
        parsed_string = parsed_string[0: start_id] + parsed_string[end_id + 9: -1]

first_level_occurrence, second_level_occurrence = 1, 1
data_list = list()
while not (first_level_occurrence == -1 or second_level_occurrence == -1):
    try:
        first_level_occurrence = parsed_string.find("aria-level")
        first_level = parsed_string[first_level_occurrence + 12]
        second_level_occurrence = parsed_string[first_level_occurrence + 10::].find("aria-level") \
                                  + first_level_occurrence + 10
        second_level = parsed_string[second_level_occurrence + 12]
        search_field = parsed_string[first_level_occurrence:second_level_occurrence]
        item_name_occurrence = search_field.find("tree-node-name")
        item_name_ends = search_field[item_name_occurrence::].find("<") + item_name_occurrence
        item_name = search_field[item_name_occurrence + 17:item_name_ends]
        data_list.append({"cur": first_level, "name": item_name, "next": second_level})
        parsed_string = parsed_string[0: first_level_occurrence] + parsed_string[second_level_occurrence - 10: -1]
    except:
        break

data_tree, list_of_current_parents = dict(), dict()
list_of_current_parents["0"] = "Root", dict()
data_tree["Root"] = dict()
current_parent = data_tree["Root"]
for instance in data_list:
    if instance['cur'] == instance['next']:
        current_parent[instance['name']] = {}
    if instance['cur'] < instance['next']:
        current_parent[instance['name']] = {}
        list_of_current_parents[instance['cur']] = current_parent
        current_parent = current_parent[instance['name']]
    if instance['cur'] > instance['next']:
        current_parent[instance['name']] = {}
        current_parent = list_of_current_parents[instance['next']]

with open(ins.name.replace("html", "json"), "w") as outfile:
    json.dump(data_tree, outfile, indent=4)
