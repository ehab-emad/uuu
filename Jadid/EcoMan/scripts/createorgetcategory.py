from django.db.models import Q
def CreateOrGetCategory(process_dict):
    '''this function creates category, group and subgroup id category was not found, this function will alway return a subgroup''' 
    from EcoMan.models import Lca_Database_Category
    from EcoMan.models import Lca_Database_Group
    from EcoMan.models import Lca_Database_Subgroup 

    query_category = Lca_Database_Category.objects.filter(Q(identifier__iexact = process_dict["category_id"]) & 
                                                          Q(name__iexact = process_dict["category_name"]) )

    query_group = Lca_Database_Group.objects.filter(Q(identifier = process_dict["group_id"]) & 
                                                    Q(name__iexact = process_dict["group_name"]) & 
                                                    Q(category_model__name__iexact = process_dict["category_name"]) &
                                                    Q(category_model__identifier__iexact = process_dict["category_id"]))                                                  

    query_subgroup = Lca_Database_Subgroup.objects.filter(Q(identifier = process_dict["subgroup_id"]) & 
                                                          Q(name__iexact = process_dict["subgroup_name"]) & 
                                                          Q(group_model__name__iexact = process_dict["group_name"]) &
                                                          Q(group_model__identifier = process_dict["group_id"]) &                                                       
                                                          Q(group_model__category_model__name__iexact = process_dict["category_name"]) &
                                                          Q(group_model__category_model__identifier__iexact = process_dict["category_id"]))                                                      
                                                      
    if query_category.exists() & query_group.exists() & query_subgroup.exists(): #nothing to create 

        return query_subgroup.get()

    if query_category.exists() & query_group.exists() & (not query_subgroup.exists()): #create subgroup
        attr_dict={'identifier': process_dict['subgroup_id'] , 'name': process_dict['subgroup_name'], 'group_model': query_group.get()}
        subgroup = Lca_Database_Subgroup(**attr_dict)
        subgroup.save()
        return subgroup

    if query_category.exists() & (not query_group.exists()) & (not query_subgroup.exists()): #create group and subgroup

        attr_dict={'identifier': process_dict['group_id'] , 'name': process_dict['group_name'], 'category_model': query_category.get()}
        group = Lca_Database_Group(**attr_dict)

        group.save()

        attr_dict={'identifier': process_dict['subgroup_id'] , 'name': process_dict['subgroup_name'], 'group_model': query_group.get()}
        subgroup = Lca_Database_Subgroup(**attr_dict)
        subgroup.save()
        return subgroup

    if (not query_category.exists()) & (not query_group.exists()) & (not query_subgroup.exists()): #create category, group and subgroup
        attr_dict={'identifier': process_dict['category_id'] , 'name': process_dict['category_name']}
        category = Lca_Database_Category(**attr_dict)
        category.save()

        attr_dict={'identifier': process_dict['group_id'] , 'name': process_dict['group_name'], 'category_model': category}
        group = Lca_Database_Group(**attr_dict)
        group.save()

        attr_dict={'identifier': process_dict['subgroup_id'] , 'name': process_dict['subgroup_name'], 'group_model': group}
        subgroup = Lca_Database_Subgroup(**attr_dict)
        subgroup.save()

        return subgroup
    return None

