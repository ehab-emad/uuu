
import json
from tkinter import filedialog as fd
#from itertools import iter
ins = fd.askopenfile()
file_to_read = open(ins.name, "r")

d= json.load (file_to_read)




def walk(e, level=2, name= "Nothing", parent ="#"):
    global l_index
    l_index+=1
    e["id"] = str(level) + '.' + str(l_index)
    e["text"] = name 
    o_dict.update({"id": str(level) + '.' + str(l_index), "parent" : parent, "text": name })
    for key in e:
        if key!="id" and key!="text":
            l_index+=1
            walk(e[key], level + 1, key, parent = e["id"])

start_level = 1
start_name = "Body"
o_dict = {}
l_index = 1 
o_dict["id"] = str(start_level) + '.' + str(l_index)
o_dict["parent"] = '#'
o_dict["text"] = start_name 

walk(d["Body"], level=0, name = next(iter(d["Body"])))





with open(ins.name + "id", "w") as outfile:
    json.dump(o_dict, outfile, indent=4)