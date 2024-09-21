
from django.db.models import Q
def import_idemat_categories():
    """This function fill Lca_Database_Category, Lca_Database_Group and Lca_Database_Subgroup based on all official Idemat LCA Databases  """
    from EcoMan.models import Lca_Database_Process
    query=Lca_Database_Process.objects.filter( (Q(database_model__accessibility="OFFICIAL_GLOBAL"))) #limited to official databases

    #collect all idemat categories of available processes
    category_dict = {}
    test =False
    for process in query:
        for category in category_dict:
            if category ==process.category_name:
                test = True
                break
        if test == False:
            category_dict[process.category_name]=process.category_id
        test = False

    #collect all idemat groups of available processes
    group_dict = {}
    test =False
    for process in query:
        for group in group_dict:
            if group ==process.group_name:
                test = True
                break
        if test == False:
            group_dict[process.group_name]=process.group_id
        test = False
  
    #collect all idemat groups of available processes
    subgroup_dict = {}
    test =False
    for process in query:
        for subgroup in subgroup_dict:
            if subgroup ==process.subgroup_name:
                test = True
                break
        if test == False:
            subgroup_dict[process.subgroup_name]=process.subgroup_id
        test = False