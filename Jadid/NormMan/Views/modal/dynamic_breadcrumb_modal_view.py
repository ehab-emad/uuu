from django.urls import reverse

def dynamic_breadcrumb_modal(category_group_object) ->str:
        dynamic_breadcrumb ='<nav aria-label="breadcrumb">'
        dynamic_breadcrumb+= '<ol class="breadcrumb">'

        li_array = []
        parent_category_group_object = category_group_object
        i = 1
        while i>0:


            path = reverse('NormMan:load_content_shared_component_create_modal')
            li_elem ='<li class="breadcrumb-item"><a class="category_group_modal" value=' + str(parent_category_group_object.UUID) + ' data-url =' + path + ' style="cursor:pointer; color:blue;"' + '>' 
            li_elem+= str(parent_category_group_object.name) + '</a></li>'
            li_array.append(li_elem)
            parent_category_group_object = parent_category_group_object.parent_group
            if parent_category_group_object == None:
                break
        for elem in reversed(li_array):
            dynamic_breadcrumb+= elem
        

        dynamic_breadcrumb+= '</ol>'
        dynamic_breadcrumb+= '</nav>'
        return dynamic_breadcrumb

def dynamic_breadcrumb_normparts_modal(category_group_object) ->str:
        dynamic_breadcrumb ='<nav aria-label="breadcrumb">'
        dynamic_breadcrumb+= '<ol class="breadcrumb">'

        li_array = []
        parent_category_group_object = category_group_object
        i = 1
        while i>0:


            path = reverse('NormMan:load_content_shared_component_norm_parts_modal')
            li_elem ='<li class="breadcrumb-item"><a class="category_group_modal" value=' + str(parent_category_group_object.UUID) + ' data-url =' + path + ' style="cursor:pointer; color:blue;"' + '>' 
            li_elem+= str(parent_category_group_object.name) + '</a></li>'
            li_array.append(li_elem)
            parent_category_group_object = parent_category_group_object.parent_group
            if parent_category_group_object == None:
                break
        for elem in reversed(li_array):
            dynamic_breadcrumb+= elem
        

        dynamic_breadcrumb+= '</ol>'
        dynamic_breadcrumb+= '</nav>'
        return dynamic_breadcrumb