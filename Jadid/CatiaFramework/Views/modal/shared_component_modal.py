import json, os
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import format_html
from EcoMan.scripts import *
from NormMan.models import *
from website.scripts import *
from website.security import check_if_user_in_groups

#qlca-----------------------------------------------------------------------------------
def shared_component_save_form(request, form, template_name, redirect = False):
    '''This function will save modal form of an existing object Analysis_Comparison
    '''
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            if request.user.is_authenticated == True:
                path_db_structure = os.path.join( "norm_parts\\db_structure\\ROOT_UUID_fd9cea85-83d8-4a79-a1f1-22d1dd578516")
                system_path = os.path.join(settings.MEDIA_ROOT)
                #before new shared component can be saved in a database a dictionary has to be created with files contained in the form
                target_category_object = get_object_or_404(Component_Group_Level, UUID = request.POST.get("target_category_uuid")) #Component_Group_Level.objects.filter(UUID =request.POST.get("target_category_uuid") ).get()                   
                target_category_object_path = os.path.join(target_category_object.data_path.path , "Shared_Components")
                #search for Shared Components and create one if does not exists
                for root, dirs, files in os.walk(os.path.join(system_path, path_db_structure)):
                    folder_to_check = os.path.join(root , "Shared_Components")
                                
                    if not os.path.exists(folder_to_check): #add 'Norm_Parts' if missing    
                        if os.path.basename(root) != "Shared_Components":
                            os.mkdir(folder_to_check)  
                new_shared_component_path = os.path.join(target_category_object_path, "EDAG_" + request.POST.get("type") + "_" +  request.POST.get("UUID")).replace("\\", "/")

                os.makedirs(new_shared_component_path, exist_ok=True)

                new_share_component = form.save()
                
                #now files can be copied from request to norman (file based) database
                if request.method == 'POST' and request.FILES.get('thumbnail') is not None:
                        actual_file = request.FILES['thumbnail']
                        fs = FileSystemStorage()
                        #To save in a specified folder
                        filename = fs.save(os.path.join(new_shared_component_path, 'thumbnail.png').replace("\\", "/"), actual_file)
                        uploaded_file_url = fs.url(filename)                 #To get the file`s url                
                        new_share_component.thumbnail = uploaded_file_url.strip("/media")

                #now files can be copied from request to norman (file based) database
                if request.method == 'POST' and request.FILES.get('stl_thumbnail') is not None:
                        actual_file = request.FILES['stl_thumbnail']
                        fs = FileSystemStorage()
                        #To save in a specified folder
                        filename = fs.save(os.path.join(new_shared_component_path, 'stl_thumbnail.stl').replace("\\", "/"), actual_file)
                        uploaded_file_url = fs.url(filename)                 #To get the file`s url                
                        new_share_component.stl_thumbnail = uploaded_file_url.strip("/media")

                #now files can be copied from request to norman (file based) database
                if request.method == 'POST' and request.FILES.get('file_catia_part') is not None:
                        actual_file = request.FILES['file_catia_part']
                        fs = FileSystemStorage()
                        #To save in a specified folder
                        filename = fs.save(os.path.join(new_shared_component_path, 'catia_part.CATPart').replace("\\", "/"), actual_file)
                        uploaded_file_url = fs.url(filename)                 #To get the file`s url                
                        new_share_component.file_catia_part = uploaded_file_url.strip("/media")

                #now files can be copied from request to norman (file based) database
                if request.method == 'POST' and request.FILES.get('file_configuration') is not None:
                        actual_file = request.FILES['file_configuration']
                        fs = FileSystemStorage()
                        #To save in a specified folder
                        filename = fs.save(os.path.join(new_shared_component_path, 'configuration.xlsx').replace("\\", "/"), actual_file)
                        uploaded_file_url = fs.url(filename)                 #To get the file`s url                
                        new_share_component.file_configuration = uploaded_file_url.strip("/media")

                #now files can be copied from request to norman (file based) database
                if request.method == 'POST' and request.FILES.get('file_workflow_json') is not None:
                        actual_file = request.FILES['file_workflow_json']
                        fs = FileSystemStorage()
                        #To save in a specified folder
                        filename = fs.save(os.path.join(new_shared_component_path, 'workflow.json').replace("\\", "/"), actual_file)
                        uploaded_file_url = fs.url(filename)                 #To get the file`s url                
                        new_share_component.file_workflow_json = uploaded_file_url.strip("/media")

                new_share_component.save()
                #now shared component can be added to category_group
                target_category_object.normparts_shared_components.add(new_share_component)
                target_category_object.save()
                
                #include shared components in all parent Component_groups        
                while True:
                    shared_component_field = getattr(target_category_object, 'normparts_shared_components')
                    shared_component_field.add(new_share_component)
                    target_category_object.save()
                    if target_category_object.parent_group: 
                        target_category_object = target_category_object.parent_group
                    else:
                        break

                #if file uploaded try to import processes 
                if request.FILES:
                    pass
                    
            data['form_is_valid'] = True
        else:
            print(form.errors.as_data())
            data['form_is_valid'] = False
            
    context.update({'form': form})
    category_group_object = Component_Group_Level.objects.filter(group_depth_level = 0).first()
    context['category_group'] = category_group_object   
    query = Component_Group_Level.objects.filter(parent_group__UUID = category_group_object.UUID)          
    context['category_groups'] = query
    from . import dynamic_breadcrumb_modal
    context['html_dynamic_breadcrumb'] = format_html(dynamic_breadcrumb_modal(category_group_object))
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)


def shared_component_modify_form(request, form, template_name, redirect = False):
    '''This function will save modal form of an existing object Analysis_Comparison
    '''
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid() or not form.new:
            if request.user.is_authenticated == True:
                path_db_structure = os.path.join( "norm_parts\\db_structure\\ROOT_UUID_fd9cea85-83d8-4a79-a1f1-22d1dd578516")
                system_path = os.path.join(settings.MEDIA_ROOT)
                #before new shared component can be saved in a database a dictionary has to be created with files contained in the form
                target_category_object = get_object_or_404(Component_Group_Level, UUID = request.POST.get("target_category_uuid")) #Component_Group_Level.objects.filter(UUID =request.POST.get("target_category_uuid") ).get()                   
                target_category_object_path = os.path.join(target_category_object.data_path.path , "Shared_Components")
                #search for Shared Components and create one if does not exists
                for root, _, _ in os.walk(os.path.join(system_path, path_db_structure)):
                    folder_to_check = os.path.join(root , "Shared_Components")
                                
                    if not os.path.exists(folder_to_check): #add 'Norm_Parts' if missing    
                        if os.path.basename(root) != "Shared_Components":
                            os.mkdir(folder_to_check)  
                new_shared_component_path = os.path.join(target_category_object_path, "EDAG_" + request.POST.get("type") + "_" +  request.POST.get("UUID")).replace("\\", "/")

                os.makedirs(new_shared_component_path, exist_ok=True)                

                new_share_component = NormParts_Shared_Component.objects.filter(UUID=request.POST.get("UUID")).get()
                # new_share_component.UUID = form.cleaned_data['UUID'] if new_share_component.UUID != form.cleaned_data['UUID'] else new_share_component.UUID
                query = NormParts_Shared_Component.objects.filter(type = "COMPONENT")
                # for new_share_component in query:
                new_share_component.name = form.cleaned_data['name'] if new_share_component.name != form.cleaned_data['name'] else new_share_component.name
                new_share_component.name_de = form.cleaned_data['name_de'] if new_share_component.name_de != form.cleaned_data['name_de'] else new_share_component.name_de
                new_share_component.oem_reference_name = form.cleaned_data['oem_reference_name'] if new_share_component.oem_reference_name != form.cleaned_data['oem_reference_name'] else new_share_component.oem_reference_name
                new_share_component.oem_reference_part_number = form.cleaned_data['oem_reference_part_number'] if new_share_component.oem_reference_part_number != form.cleaned_data['oem_reference_part_number'] else new_share_component.oem_reference_part_number
                new_share_component.accessibility = form.cleaned_data['accessibility'] if new_share_component.accessibility != form.cleaned_data['accessibility'] else new_share_component.accessibility
                new_share_component.project_model = form.cleaned_data['project_model'] if new_share_component.project_model != form.cleaned_data['project_model'] else new_share_component.project_model

                # -> Other information has to follow then.                

                # new_share_component = form.save()
                
                # now files can be copied from request to norman (file based) database
                if request.method == 'POST' and request.FILES.get('thumbnail') is not None:
                        actual_file = request.FILES['thumbnail']
                        fs = FileSystemStorage()
                        #To save in a specified folder
                        filename = fs.save(os.path.join(new_shared_component_path, 'thumbnail.jpg').replace("\\", "/"), actual_file)
                        uploaded_file_url = fs.url(filename)                 #To get the file`s url                
                        new_share_component.thumbnail = uploaded_file_url.strip("/media")

                #now files can be copied from request to norman (file based) database
                if request.method == 'POST' and request.FILES.get('stl_thumbnail') is not None:
                        actual_file = request.FILES['stl_thumbnail']
                        fs = FileSystemStorage()
                        #To save in a specified folder
                        filename = fs.save(os.path.join(new_shared_component_path, 'stl_thumbnail.stl').replace("\\", "/"), actual_file)
                        uploaded_file_url = fs.url(filename)                 #To get the file`s url                
                        new_share_component.stl_thumbnail = uploaded_file_url.strip("/media")

                #now files can be copied from request to norman (file based) database
                if request.method == 'POST' and request.FILES.get('file_catia_part') is not None:
                        actual_file = request.FILES['file_catia_part']
                        fs = FileSystemStorage()
                        #To save in a specified folder
                        filename = fs.save(os.path.join(new_shared_component_path, 'catia_part.CATPart').replace("\\", "/"), actual_file)
                        uploaded_file_url = fs.url(filename)                 #To get the file`s url                
                        new_share_component.file_catia_part = uploaded_file_url.strip("/media")

                #now files can be copied from request to norman (file based) database
                if request.method == 'POST' and request.FILES.get('file_configuration') is not None:
                        actual_file = request.FILES['file_configuration']
                        fs = FileSystemStorage()
                        #To save in a specified folder
                        filename = fs.save(os.path.join(new_shared_component_path, 'configuration.xlsx').replace("\\", "/"), actual_file)
                        uploaded_file_url = fs.url(filename)                 #To get the file`s url                
                        new_share_component.file_configuration = uploaded_file_url.strip("/media")

                #now files can be copied from request to norman (file based) database
                if request.method == 'POST' and request.FILES.get('file_workflow_json') is not None:
                        actual_file = request.FILES['file_workflow_json']
                        fs = FileSystemStorage()
                        #To save in a specified folder
                        filename = fs.save(os.path.join(new_shared_component_path, 'workflow.json').replace("\\", "/"), actual_file)
                        uploaded_file_url = fs.url(filename)                 #To get the file`s url                
                        new_share_component.file_workflow_json = uploaded_file_url.strip("/media")

                new_share_component.save()
                #now shared component can be added to category_group

                # -> Target group will have to be modified

                target_category_object.normparts_shared_components.add(new_share_component)
                target_category_object.save()
                
                #include shared components in all parent Component_groups        
                while True:
                    shared_component_field = getattr(target_category_object, 'normparts_shared_components')
                    shared_component_field.add(new_share_component)
                    target_category_object.save()
                    if target_category_object.parent_group: 
                        target_category_object = target_category_object.parent_group
                    else:
                        break

                #if file uploaded try to import processes 
                if request.FILES:
                    pass
                    
            data['form_is_valid'] = True
        else:
            print(form.errors.as_data())
            data['form_is_valid'] = False
            
    context.update({'form': form})
    category_group_object = Component_Group_Level.objects.filter(UUID = form.target_uuid).first()
    context['category_group'] = category_group_object   
    query = Component_Group_Level.objects.filter(parent_group__UUID = category_group_object.UUID)          
    context['category_groups'] = query
    from . import dynamic_breadcrumb_modal
    context['html_dynamic_breadcrumb'] = format_html(dynamic_breadcrumb_modal(category_group_object))
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def shared_component_create_modal(request):
    from NormMan.forms.modal import NewSharedComponentForm
    if request.user.is_authenticated == True:    
        if request.method == 'POST':            
            target_category_object = get_object_or_404(Component_Group_Level, UUID = request.POST.get("target_category_uuid")) #Component_Group_Level.objects.filter(UUID =request.POST.get("target_category_uuid") ).get()                   
            target_category_object_path = os.path.join(target_category_object.data_path.path , "Shared_Components")
            new_shared_component_path = os.path.join(target_category_object_path, "EDAG_" + request.POST.get("type") + "_" +  request.POST.get("UUID")).replace("\\", "/")
            new_post = request.POST.copy()
            new_post.update({'data_path': new_shared_component_path})
            form = NewSharedComponentForm(new_post, files=request.FILES)
            new_list = []
            new_list.append((request.POST.get('project_model'), request.POST.get('project_model')))
            form.fields['project_model'].widget.choices = new_list
        else:
            form = NewSharedComponentForm(request = request,)
            #user can only select project for which he has access
            authorised_projects = request.user.projectuser.authorised_projects.all()
            new_list = []            
            for project in authorised_projects:
                username = project.owner.username if project.owner is not None else "Undefined user"
                new_list.append((str(project.UUID), "ID: " + str(project.UUID) + " Name: " + project.name + " Owner: " + username))
            form.fields['project_model'].widget.choices = new_list
            form.fields['project_model'].initial = [request.user.projectuser.sandbox_project_id]
    return shared_component_save_form(request, form, 'modal/shared_component/shared_component_create_modal.html', redirect=False)

def shared_component_modify_modal(request, parent:str = None, uuid:str = None) -> JsonResponse:
    from NormMan.forms.modal import NewSharedComponentForm
    if request.user.is_authenticated == True:    
        if request.method == 'POST':            
            target_category_object = get_object_or_404(Component_Group_Level, UUID = request.POST.get("target_category_uuid")) #Component_Group_Level.objects.filter(UUID =request.POST.get("target_category_uuid") ).get()                   
            target_category_object_path = os.path.join(target_category_object.data_path.path , "Shared_Components")
            new_shared_component_path = os.path.join(target_category_object_path, "EDAG_" + request.POST.get("type") + "_" +  request.POST.get("UUID")).replace("\\", "/")
            new_post = request.POST.copy()
            new_post.update({'data_path': new_shared_component_path})
            form = NewSharedComponentForm(new_post, parent = parent, uuid = uuid, files=request.FILES)
            new_list = []
            new_list.append((request.POST.get('project_model'), request.POST.get('project_model')))
            form.fields['project_model'].widget.choices = new_list
        else:
            form = NewSharedComponentForm(request = request, parent = parent, uuid = uuid)
            #user can only select project for which he has access
            authorised_projects = request.user.projectuser.authorised_projects.all()
            new_list = []
            for project in authorised_projects:
                username = project.owner.username if project.owner is not None else "Undefined user"
                new_list.append((str(project.UUID), "ID: " + str(project.UUID) + " Name: " + project.name + " Owner: " + username))
            initial_project = form.fields['project_model'].initial.UUID
            form.fields['project_model'].widget.choices = new_list
            form.fields['project_model'].initial = [initial_project]
    return shared_component_modify_form(request, form, 'modal/shared_component/shared_component_modify_modal.html', redirect=False)


def load_content_shared_component_create_modal(request):
    '''View used to reload content in the dashboard
    '''

    trigger_id = request.GET['trigger_id']


    context={}
    data={}
    root_group = None

    #Button search was pressed
    if trigger_id == 'search_submit':
        if request.method == 'GET' and 'object_name' in request.GET:
            object_name = request.GET['object_name'].strip()
            object_name =object_name[18:]
        else:
            object_name = None
             
        interactive_categories = {
            "TAILGATE": "512052b1-38df-4040-abdd-14edafc06b3e",
            "TUER": "421017fa-0519-41e3-bd32-9c57019a8e17"
        }
        category_id = interactive_categories[object_name]
        if object_name in interactive_categories.keys():
            current_category_group = Component_Group_Level.objects.filter(UUID =category_id).get()
        else:
            current_category_group = None


    #Category card was clicked
    if trigger_id == 'switch_category':
        category_id = request.GET['category_id']
        current_category_group = Component_Group_Level.objects.filter(UUID = category_id).get()

    query = Component_Group_Level.objects.filter(parent_group__UUID = category_id)          
    context_category_groups={}  
    context_category_groups['category_groups'] = query
    context_category_groups['category_group'] = current_category_group
    from . import dynamic_breadcrumb_modal
    context_category_groups['html_dynamic_breadcrumb'] = format_html(dynamic_breadcrumb_modal(current_category_group))
    data['html_category_groups'] =render_to_string('modal//shared_component//cards_category_group_children.html', context_category_groups, request=request)


    if root_group:
        p = os.path.join( settings.MEDIA_ROOT, root_group.data_path.name, "meta_threejs.json" )
        f = open(p, "r")    
        content = json.load(f)
        data['json_tree'] = content
    else:
        data['json_tree'] = None
    return JsonResponse(data)

def shared_component_delete_modal(request, uuid):
    shared_component = get_object_or_404(NormParts_Shared_Component, UUID = uuid)
    data=dict()
    if request.method == 'POST':
        if (shared_component.owner_id == request.user.id) or check_if_user_in_groups(request,['/be_paramount/app_normman/user-professional']):
            shared_component.delete()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False

    else:
        context = {'shared_component': shared_component}
        data['html_form'] = render_to_string('modal/shared_component/shared_component_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)