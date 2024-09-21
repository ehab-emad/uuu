from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from EcoMan.models import Lca_Part
from EcoMan.models import Lca_Database_Process
from EcoMan.models import Lca_Database
from EcoMan.models import Instance_Idemat_Database_Process
from EcoMan.models import Lca_Database_Category
from EcoMan.models import Lca_Database_Group
from EcoMan.models import Lca_Database_Subgroup, Analysis_Comparison, Analysis
from django.db.models import Q
from django.shortcuts import render
from website.generate_pk import check_pk
import copy

def lca_part_add_process_instance(request, pk_lca_part, lca_step, weight_unit):
    '''Add Process
    '''
    lca_part = get_object_or_404(Lca_Part, pk=pk_lca_part )
   
    if request.method == 'POST':
        POST_copy = request.POST.copy()
        POST_copy.update({'id': lca_part.id}) #add id since this field is required but it is meaningless for the user during creation

        from EcoMan.forms import Lca_Part_Add_Process_Form
        form = Lca_Part_Add_Process_Form(POST_copy, instance=lca_part)
    else:
        from EcoMan.forms import Lca_Part_Add_Process_Form
        form = Lca_Part_Add_Process_Form(instance=lca_part)
        #collect all available  databases
        database_open=Lca_Database.objects.filter(accessibility="OPEN") #not restricted access
        database_organisation=Lca_Database.objects.filter(accessibility="ORGANISATION") #not restricted access for every user of the corporation   
        database_project=Lca_Database.objects.filter(accessibility="PROJECT")

        #exclude databases which are archived
        database_open = database_open.filter(is_archive = False)
        database_organisation = database_organisation.filter(is_archive = False)
        database_project = database_project.filter(is_archive = False)

        auth_project_ids = []
        for project in request.user.projectuser.authorised_projects.all():
            auth_project_ids.append(project.UUID)
        database_project = database_project.filter(projects__UUID__in = auth_project_ids)

        database_dict = {}
        for database in database_open:
            database_dict[database.name + " " + database.accessibility] = database.id

        for database in database_organisation:
            database_dict[database.name + " " + database.accessibility] = database.id
        #project database can be only used within project analyses!
        for database in database_project:
            for project in database.projects.all():
                if request.user.projectuser.current_project.UUID == project.UUID:
                    database_dict[database.name + " " + database.accessibility] = database.id



        #collect all available  categories
        category_query=Lca_Database_Category.objects.all() 
        category_dict = {}
        for category in category_query:
            category_dict[category.identifier + " " + category.name] = database.id

        choices_list =[]
        choices_list.append((0,"Please select LCA Database"))
        choices_list= choices_list + [(database_dict[x], x) for x in database_dict]
        form.fields['lca_database_choice'].choices = choices_list

        choices_list =[]
        choices_list.append((0,"Please select LCA Category"))
        choices_list= choices_list + [(category_dict[x], x) for x in category_dict]
        form.fields['lca_category_choice'].choices = choices_list

        form.fields['lca_group_choice'].choices=[(0,"Please select LCA Group")]
        form.fields['lca_subgroup_choice'].choices=[(0,"Please select LCA Subgroup")]
        form.fields['lca_process_choice'].choices=[(0, "Please select LCA Process")]
  
    return lcastep_save_form(request, form, 'modals/lca_part/lca_part_add_process.html', lca_step = lca_step, weight_unit = weight_unit)


#lcastep_save_form-----------------------------------------------------------------------------------
def lcastep_save_form(request, form, template_name, lca_step, weight_unit):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            lca_part = get_object_or_404(Lca_Part, pk=form.data['id'])

            if request.POST.get('lca_process_choice'):
                idemat_process_orig = get_object_or_404(Lca_Database_Process, pk=request.POST['lca_process_choice'])
                idemat_process_new = copy.copy(idemat_process_orig)
                idemat_process_new.id = None
                idemat_process_new.pk = None                
                idemat_process_new.save()
                instance_process_model=Instance_Idemat_Database_Process()
                instance_process_model.process_model=idemat_process_orig
                instance_process_model.calculation_model=idemat_process_new
                instance_process_model.calculation_model.accessibility = "HIDDEN"
                instance_process_model.calculation_model.save()
                instance_process_model.results_model.accessibility = "HIDDEN" 
                instance_process_model.results_model.save()   
                instance_process_model.name = idemat_process_orig.name
                instance_process_model.lca_step = lca_step
                instance_process_model.process_quantity=request.POST['quantity']
                instance_process_model.save()
                lca_part.lca_process_model.add(instance_process_model)   
                lca_part.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    context['lca_step'] = lca_step
    context['weight_unit'] = weight_unit
    #retrieve information about analysis and weight units from settings. Required for context in quantity and warning messeage about units
    if form.instance.analysis_Upstream.first().analysis_settings.weight_units == 'KILOGRAMS':
        context['target_unit']  = 'kg'

    

    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

#lcastep_save_process_form-----------------------------------------------------------------------------------
def lcastep_save_process_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            qlcastep = get_object_or_404(Lca_Part, pk=request.POST['id'])

            if request.POST.get('Idemat_Process'):
                idemat_process = get_object_or_404(Lca_Database_Process, pk=request.POST['Idemat_Process'])
                instance_process_idemat_model=Instance_Idemat_Database_Process()
                instance_process_idemat_model.process_model=idemat_process
                instance_process_idemat_model.process_quantity=request.POST['quantity']
                instance_process_idemat_model.save()
                qlcastep.process_instance_idemat_model.add(instance_process_idemat_model)   
                qlcastep.save()              
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)
#lcastep_save_process_circularity_form-----------------------------------------------------------------------------------
def lcastep_save_process_circularity_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            qlcastep = get_object_or_404(Lca_Part, pk=request.POST['id'])

            if request.POST.get('Idemat_Process'):
                idemat_process = get_object_or_404(Lca_Database_Process, pk=request.POST['Idemat_Process'])
                instance_process_idemat_model=Instance_Idemat_Database_Process()
                instance_process_idemat_model.process_model=idemat_process
                instance_process_idemat_model.process_quantity=request.POST['quantity']
                instance_process_idemat_model.save()
                qlcastep.process_instance_circularity_idemat_model.add(instance_process_idemat_model)   
                qlcastep.save()              
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)
#lcastep_save_transport_form-----------------------------------------------------------------------------------
def lcastep_save_transport_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            qlcastep = get_object_or_404(Lca_Part, pk=request.POST['id'])
                
            if request.POST.get('Idemat_Transport'):
                idemat_process = get_object_or_404(Lca_Database_Process, pk=request.POST['process_choice'])
                instance_transport_idemat_model=Instance_Idemat_Database_Process()
                instance_transport_idemat_model.process_model=idemat_process
                instance_transport_idemat_model.process_weight=qlcastep.part_model.weight
                instance_transport_idemat_model.process_quantity=float(request.POST['quantity']) * instance_transport_idemat_model.process_weight /1000
                instance_transport_idemat_model.save()
                qlcastep.transport_instance_idemat_model.add(instance_transport_idemat_model)   
                qlcastep.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

#qlcastep_save_transport_cicularity_form-----------------------------------------------------------------------------------
def qlcastep_save_transport_cicularity_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            qlcastep = get_object_or_404(Lca_Part, pk=request.POST['id'])
                
            if request.POST.get('Idemat_Transport'):
                idemat_process = get_object_or_404(Lca_Database_Process, pk=request.POST['Idemat_Transport'])
                instance_transport_idemat_model=Instance_Idemat_Database_Process()
                instance_transport_idemat_model.process_model=idemat_process
                instance_transport_idemat_model.process_weight=qlcastep.part_model.weight
                instance_transport_idemat_model.process_quantity=float(request.POST['quantity']) * instance_transport_idemat_model.process_weight /1000
                instance_transport_idemat_model.save()
                qlcastep.transport_instance_circularity_idemat_model.add(instance_transport_idemat_model)   
                qlcastep.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)



#Add Process for circularity
def step1upstream_add_process_circularity(request, pk):
    step1upstream = get_object_or_404(Lca_Part, pk=pk)
    process_query=Lca_Database_Process.objects.filter(Q(category_model__identifier="D") | Q(category_model__identifier="F")).exclude(unit__icontains="s")   #excluded processes with funky units

    from EcoMan.forms import Step1UpstreamForm_Process #this should be renamed to Lca_Part_Add_Process_Form


    if request.method == 'POST':
        form = Step1UpstreamForm_Process(request.POST, instance=step1upstream)
    else:
        form = Step1UpstreamForm_Process(instance=step1upstream)
    form.fields['Idemat_Process'].choices=[(x.id, x.name + "     Unit: [" + x.unit + "]") for x in process_query]
    return lcastep_save_process_circularity_form(request, form, 'modals/qlca/step1upstream_add_process_circularity.html')



#Add Transport for circularity
def step1upstream_add_transport_circularity(request, pk):
    step1upstream = get_object_or_404(Lca_Part, pk=pk)
    transport_query=Lca_Database_Process.objects.filter(category_model__identifier="C", unit__icontains="tkm") #limited to transport based on tkm
    from EcoMan.forms import Step1UpstreamForm_Transport #this should be renamed to Lca_Part_Add_Material_Form
    if request.method == 'POST':
        form = Step1UpstreamForm_Transport(request.POST, instance=step1upstream)
    else:
        form = Step1UpstreamForm_Transport(instance=step1upstream)
    form.fields['Idemat_Transport'].choices=[(x.id, x.name + "     Unit: [" + x.unit + "]") for x in transport_query]
    return qlcastep_save_transport_cicularity_form(request, form, 'modals/qlca/step1upstream_add_transport_circularity.html')

#Add Utilisation
# def step1upstream_add_utilisation(request, pk):
#     step3downstream = get_object_or_404(Lca_Part, pk=pk)
#     user = request.user
#     vehicles_query=Vehicle.objects.filter(owner=user) 
#     from EcoMan.forms import UtilisationInstanceCreateForm
#     if request.method == 'POST':
#         form = UtilisationInstanceCreateForm(request.POST, instance=step3downstream)
#     else:
#         form = UtilisationInstanceCreateForm(instance=step3downstream)
#     form.fields['vehicle'].choices=[(x.id, x.name) for x in vehicles_query]
#     return qlcastepdownstream_save_form(request, form, 'modals/qlca/step1upstream_add_utilisation.html')




#Delete
def step1upstream_delete(request, pk):
    step1upstream = get_object_or_404(Lca_Part, pk=pk)
    data = dict()
    if request.method == 'POST':
        step1upstream.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code

    else:
        context = {'step1upstream': step1upstream}
        data['html_form'] = render_to_string('modals/qlca/step1upstream_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)


def load_lca_database_processes(request):
    '''View used to reload dropdown list during addition of idemat material process
    '''
    #identify analysis_comparison_id
    str = request.META['HTTP_REFERER']
    
       
    analysis_id = [check_pk(chunk) for chunk in str.split("/") if check_pk(chunk)][0] #Adam
    analysis_object = Analysis_Comparison.objects.filter(pk= analysis_id )

    if not analysis_object:
         analysis_object = Analysis.objects.filter(pk= analysis_id )
    if analysis_object:         
        analysis_object= analysis_object.get()
    trigger_id = request.GET['trigger_id']

    if request.method == 'GET' and 'database_id' in request.GET:
        database_id = int(request.GET['database_id'].strip() or 0)
    else:
        database_id = 0

    if request.method == 'GET' and 'category_id' in request.GET:
        category_id = int(request.GET['category_id'].strip() or 0)
    else:
        category_id = 0

    if request.method == 'GET' and 'group_id' in request.GET:
        group_id = int(request.GET['group_id'].strip() or 0)
    else:
        group_id = 0

    if request.method == 'GET' and 'subgroup_id' in request.GET:
        subgroup_id = int(request.GET['subgroup_id'].strip() or 0)
    else:
        subgroup_id = 0

    if request.method == 'GET' and 'process_id' in request.GET:
        process_id = int(request.GET['process_id'].strip() or 0)
    else:
        process_id = 0

    quantity = float(request.GET['quantity'].strip() or 0)

    context={}

   #process search  (ul -> li option) was selected
    if trigger_id == 'option_submit':

        lca_process_object = get_object_or_404(Lca_Database_Process, pk=process_id)
        lca_database = lca_process_object.database_model
        lca_category = lca_process_object.category_model
        lca_process_group = lca_process_object.group_model
        lca_process_subgroup = lca_process_object.subgroup_model

        #database field
        choices_list= [(lca_database.id,  f' {lca_database.name:} {lca_database.accessibility} ') ]
        context['lca_databases']=choices_list

        #category field
        choices_list= [(lca_category.id,  f' [{lca_category.id:}] {lca_category.name} ') ]
        context['lca_categories']=choices_list

        #group field
        choices_list= [(lca_process_group.id,  f' [{lca_process_group.id:}] {lca_process_group.name} ') ]
        context['lca_groups']=choices_list

        #subgroup field
        choices_list= [(lca_process_subgroup.id,  f' [{lca_process_subgroup.id:}] {lca_process_subgroup.name} ') ]
        context['lca_subgroups']=choices_list

        #process field
        choices_list= [(lca_process_object.id,  f'{lca_process_object.name} GsWP: {lca_process_object.carbon_footprint:.2f}') ]
        context['lca_processes']=choices_list


        context['selected_process_preview']=lca_process_object
        data={}
        data['lca_databases'] = render_to_string('modals/lca_part/dropdown_list_options/lca_database_dropdown_list_options.html', context, request=request)
        data['lca_categories'] = render_to_string('modals/lca_part/dropdown_list_options/lca_category_dropdown_list_options.html', context, request=request)
        data['lca_groups'] = render_to_string('modals/lca_part/dropdown_list_options/lca_group_dropdown_list_options.html', context, request=request)
        data['lca_subgroups'] = render_to_string('modals/lca_part/dropdown_list_options/lca_subgroup_dropdown_list_options.html', context, request=request)
        data['lca_processes'] = render_to_string('modals/lca_part/dropdown_list_options/lca_process_dropdown_list_options.html', context, request=request)
        data['html_process_preview'] =render_to_string('modals/lca_part/lca_process_preview_modal_content.html', context, request=request)
        context['target_unit']  = analysis_object.analysis_settings.weight_units 
        return JsonResponse(data)

   #Button search was pressed
    if trigger_id == 'search_submit':
        search_text = request.GET['search_text']

        #searching will be limited selected LCA Database
        #limited to processs GWP based on kgs
        if category_id == 0:
            process_query=Lca_Database_Process.objects.filter(Q(database_model_id = database_id))  
        else:
            process_query=Lca_Database_Process.objects.filter(Q(database_model_id = database_id) & Q(category_model_id = category_id))     

        process_query = process_query.filter(Q(accessibility = 'PRIVATE') | Q(accessibility = 'DATABASE_USERS') )
        process_query = process_query.filter(name__icontains=search_text)  
        context['search_result']=process_query     
        data={}        
        data['html_process_preview'] =render_to_string('modals/lca_part/lca_process_preview_modal_content.html', context, request=request)

        return JsonResponse(data)

   #Button reset was pressed
    if trigger_id == 'reset_modal':
        context={}
        choices_list =[]

        #database field
        database_open=Lca_Database.objects.filter(accessibility="OPEN") #not restricted access
        database_organisation=Lca_Database.objects.filter(accessibility="ORGANISATION") #not restricted access for every user of the corporation   
        database_project=Lca_Database.objects.filter(accessibility="PROJECT")

        #exclude databases which are archived
        database_open = database_open.filter(is_archive = False)
        database_organisation = database_organisation.filter(is_archive = False)
        database_project = database_project.filter(is_archive = False)

        auth_project_ids = []
        for project in request.user.projectuser.authorised_projects.all():
            auth_project_ids.append(project.UUID)
        database_project = database_project.filter(projects__UUID__in = auth_project_ids)
        database_dict = {}
        for database in database_open:
            database_dict[database.id + " " + database.name + " " + database.note] = database.id

        for database in database_organisation:
            database_dict[database.id + " " + database.name + " " + database.note] = database.id
        #project database can be only used within project analyses!
        for database in database_project:
            for project in database.projects.all():
                if request.user.projectuser.current_project.UUID == project.UUID:
                    database_dict[database.id + " " + database.name + " " + database.note] = database.id



        #collect all available  categories
        category_query=Lca_Database_Category.objects.all() 
        category_dict = {}
        for category in category_query:
            category_dict[category.identifier + " " + category.name] = database.id

        choices_list =[]
        choices_list.append((0,"Please select LCA Database"))
        choices_list= choices_list + [(database_dict[x], x) for x in database_dict]       
        context['lca_databases']=choices_list 

        #category field
        choices_list= [(0,  f"Please select LCA Category") ]
        context['lca_categories']=choices_list

        #group field
        choices_list= [(0,  f"Please select LCA Group") ]
        context['lca_groups']=choices_list

        #subgroup field
        choices_list= [(0,  f"Please select LCA Subgroup") ]
        context['lca_subgroups']=choices_list

        #process field
        choices_list= [(0,  f"Please select LCA Process") ]
        context['lca_processes']=choices_list


    
        data={}        
        data['lca_databases'] = render_to_string('modals/lca_part/dropdown_list_options/lca_database_dropdown_list_options.html', context, request=request)
        data['lca_categories'] = render_to_string('modals/lca_part/dropdown_list_options/lca_category_dropdown_list_options.html', context, request=request)
        data['lca_groups'] = render_to_string('modals/lca_part/dropdown_list_options/lca_group_dropdown_list_options.html', context, request=request)
        data['lca_subgroups'] = render_to_string('modals/lca_part/dropdown_list_options/lca_subgroup_dropdown_list_options.html', context, request=request)
        data['lca_processes'] = render_to_string('modals/lca_part/dropdown_list_options/lca_process_dropdown_list_options.html', context, request=request)
        data['html_process_preview'] =render_to_string('modals/lca_part/lca_process_preview_modal_content.html', context, request=request)
        return JsonResponse(data)


    #Button refresh_table was pressed
    if trigger_id == 'refresh_table':
        if process_id: #if material was selected
            context={}
            context['selected_process_preview']=get_object_or_404(Lca_Database_Process, pk=process_id)

            #make simple multiplications to give estimations for given value
            context['selected_process_result']={}
            context['selected_process_result']['environmental_footprint']=context['selected_process_preview'].carbon_footprint * quantity
            context['selected_process_result']['ced_total']=context['selected_process_preview'].carbon_footprint * quantity
            context['selected_process_result']['carbon_footprint']=context['selected_process_preview'].carbon_footprint * quantity
            context['target_unit']  = analysis_object.analysis_settings.weight_units 
        data={}
        data['html_process_preview'] =render_to_string('modals/lca_part/lca_process_preview_modal_content.html', context, request=request)
        return JsonResponse(data)

    #Dropdown option Lca Database was changed
    if trigger_id == 'id_lca_database_choice':
        
        #available categories over process search

        database_object = get_object_or_404(Lca_Database, pk=database_id)
        category_list = []         
        #category_list.extend([(c.id, "[" + str(c.id) + "]" + c.name) for c in database_object.categories.all() if (c.id, c.name) not in category_list])
        category_list.extend([(c.id, f"[{c.id}] {c.name}") for c in database_object.categories.all()])
        choices_list =[]
        choices_list.append((0,"Please select LCA Category"))
        choices_list= choices_list + [(key, value) for key, value in category_list]
        context['lca_categories']=choices_list
        data={}
        data['lca_categories'] = render_to_string('modals/lca_part/dropdown_list_options/lca_category_dropdown_list_options.html', context, request=request)
        return JsonResponse(data)

    #Dropdown option Lca Category was changed
    if trigger_id == 'id_lca_category_choice':

        group_list = list(Lca_Database_Group.objects.filter(Q(category_model__id = category_id)))
                                                                   
        choices_list =[]
        choices_list.append((0,"Please select LCA Group"))
        choices_list= choices_list + [(x.id,  f"[{x.id}] {x.name}")for x in group_list]
        context['lca_groups']=choices_list
        data={}
        data['lca_groups'] = render_to_string('modals/lca_part/dropdown_list_options/lca_group_dropdown_list_options.html', context, request=request)
        return JsonResponse(data)

    #Dropdown option Lca Group was changed
    if trigger_id == 'id_lca_group_choice':
        choices_list =[]
        choices_list.append((0,"Please select LCA Process Subgroup"))
        if database_id != 0 and group_id!=0: #User has selected process group reload process list
            subgroup_list = list(Lca_Database_Subgroup.objects.filter((Q(group_model_id=group_id))))
            choices_list= choices_list + [(x.id, f"[{x.id}] {x.name}") for x in subgroup_list]
            context['lca_subgroups']=choices_list
        data={}
        data['lca_subgroups'] = render_to_string('modals/lca_part/dropdown_list_options/lca_subgroup_dropdown_list_options.html', context, request=request)
        return JsonResponse(data)


    #Dropdown option Lca SubGroup was changed
    if trigger_id == 'id_lca_subgroup_choice':
        choices_list =[]
        choices_list.append((0,"Please select LCA Process"))
        if database_id != 0 and group_id!=0 and subgroup_id!=0: #User has selected process subgroup reload process list
            query = Lca_Database_Process.objects.filter((Q(group_model_id=group_id) 
                                                                     & Q(subgroup_model_id=subgroup_id) 
                                                                     & Q(database_model_id=database_id) 
                                                        ))
            #check if job is private
            if analysis_object.analysis_settings.is_public:
                query = query.filter(Q(accessibility = "DATABASE_USERS") )
            else:
                query = query.filter(Q(accessibility = "DATABASE_USERS") | Q(accessibility = "PRIVATE")  )                

            process_list = list(query)
            choices_list= choices_list + [(x.id,  f"[{x.id}] {x.name}")for x in process_list]
            context['lca_processes']=choices_list
        data={}
        data['lca_processes'] = render_to_string('modals/lca_part/dropdown_list_options/lca_process_dropdown_list_options.html', context, request=request)
        return JsonResponse(data)
 


    #Dropdown option Process was changed
    if trigger_id == 'id_lca_process_choice':
        if group_id != 0 and process_id != 0: #User has selected process reload process preview 
            #generate dummy object 
            context['selected_process_preview']=get_object_or_404(Lca_Database_Process, pk=process_id)
            template_to_render ='modals/lca_part/lca_process_preview_modal_content.html'
        data={}
        data['html_process_preview'] =render_to_string('modals/lca_part/lca_process_preview_modal_content.html', context, request=request)
        return JsonResponse(data)