


import pandas as pd
from django.contrib.staticfiles.storage import staticfiles_storage



def import_idemat():

    path_to_excel_template = 'EcoMan/Idemat_2022RevA_Hubert.xls'
    
    template_excel_file = staticfiles_storage.path(path_to_excel_template)
    
    df = pd.read_excel (template_excel_file, sheet_name='Idemat2022', header=0,  usecols="A:V", dtype={'idemat_id_group':'string','idemat_id_subgroup':'string'})

    category_dict=dict()
    group_dict=dict()
    subgroup_dict=dict()
    process_dict=dict()
    category=[]
    group=[]
    subgroup=[]
    process=[]
    i=0
    for x in df.index:
        row_data = df.iloc[x].to_dict()

        #serch for processes
        keys = [ 'unit', 'ec_total', 'ec_of_human_health', 'ec_exo_toxicity', 'ec_resource', 
                 'ec_carbon', 'carbon_footprint', 'ced_total', 'recipe2016_endpoint', 'recipe_human_health', 
                'recipe_eco_toxicity', 'recipe_resources', 'environmental_footprint', 'source']
        keys.extend(['category_id', 'category_name','group_id', 'group_name', 'subgroup_id', 'subgroup_name','process_id','process_name',])

        process_dict = {y:row_data[y] for y in keys}

        if process_dict in process:
            pass
        else:
           process.append(process_dict)
           print('New Item Found! ', process_dict['process_id'] )

    return process

#import_idemat()


def import_idemat_separated():   #use this import when you want to have structured database logic with category group subgroup and process with usage of foreign keys

    df = pd.read_excel (r'C:\Users\hr63674\Desktop\Idemat_2022RevA_Hubert.xlsx', sheet_name='Idemat2022', header=0,  usecols="A:V", dtype={'idemat_id_group':'string','idemat_id_subgroup':'string'})

    category_dict=dict()
    group_dict=dict()
    subgroup_dict=dict()
    process_dict=dict()
    category=[]
    group=[]
    subgroup=[]
    process=[]
    i=0
    for x in df.index:
        row_data = df.iloc[x].to_dict()

        #serch for categories
        keys = ['category_id', 'category_name']
        category_dict = {y:row_data[y] for y in keys}
        if category_dict in category:
            pass
        else:
           category.append(category_dict)
           print('New Item Found! ', category_dict )

        #serch for groups
        keys = ['group_id', 'group_name']
        group_dict = {y:row_data[y] for y in keys}
        group_dict['ForeignKey']=category_dict
        if group_dict in group:
            pass
        else:
           group.append(group_dict)
           print('New Item Found! ', group_dict )

        #serch for subgroups
        keys = ['subgroup_id', 'subgroup_name']
        subgroup_dict = {y:row_data[y] for y in keys}
        subgroup_dict['ForeignKey']=group_dict
        if subgroup_dict in subgroup:
            pass
        else:
           subgroup.append(subgroup_dict)
           print('New Item Found! ', subgroup_dict )

        #serch for processes
        keys = ['process_id', 'unit',  'ec_total', 'ec_of_human_health', 'ec_exo_toxicity', 'ec_resource', 
                'process_name', 'ec_carbon', 'carbon_footprint', 'ced_total', 'recipe2016_endpoint', 'recipe_human_health', 
                'recipe_eco_toxicity', 'recipe_resources', 'environmental_footprint', 'source']
        process_dict = {y:row_data[y] for y in keys}
        process_dict['ForeignKey']=subgroup_dict
        if process_dict in process:
            pass
        else:
           process.append(process_dict)
           print('New Item Found! ', process_dict['process_id'] )

    return process

#import_idemat_separated()


