import os, shutil
from tkinter import filedialog as fd
ins = fd.askdirectory()


for root, dirs, files in os.walk(ins):
    folder_to_check = os.path.join(root , "Norm_Parts")
    folder_new_name = os.path.join(root , "Shared_Components")     
    if os.path.exists(folder_to_check):

        if os.path.basename(root) != "Norm_Parts":
            #os.rename(folder_to_check, folder_new_name)
            shutil.move(folder_to_check, folder_new_name) 
    else:
        pass   
    for filename in files:
        pass
    for dirname in dirs:
        pass



