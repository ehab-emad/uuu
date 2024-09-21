from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from EcoMan.models import Lca_Database_Process
from EcoMan.models import  Lca_Database
from EcoMan.models import Lca_Database_Group
from EcoMan.models import Lca_Database_Subgroup
from django.shortcuts import render
from website.security import check_if_user_in_groups
#Please note that "idemat_process" should be renamed to "eco_process" as processes can be as well created from client

#idemat_process-----------------------------------------------------------------------------------
def lca_process_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def lca_process_create(request, lca_database_pk = None):
    from EcoMan.forms import EcoProcessCreateForm

    if request.method == 'POST':
        form = EcoProcessCreateForm(request.POST)
    else:
        if lca_database_pk:
            database = get_object_or_404(Lca_Database, pk=lca_database_pk)
            request.idemat_database = database
        form = EcoProcessCreateForm(request = request)
        #we have to remove options which shouldnt be selected from user  (archive and hidden)
        tuple_to_delete = form.fields['accessibility'].widget.choices[2]
        form.fields['accessibility'].widget.choices.remove(tuple_to_delete)
        tuple_to_delete = form.fields['accessibility'].widget.choices[2]
        form.fields['accessibility'].widget.choices.remove(tuple_to_delete)
    return lca_process_save_form(request, form, 'modals/lca_process/lca_process_create_modal.html')

def lca_process_update(request, pk):
    '''if process belong to the logged user or or user is a project owner or user is staff member process can be edited '''
    idemat_database_process = get_object_or_404(Lca_Database_Process, pk=pk)
    from EcoMan.forms import EcoProcessEditForm
    database_owner = idemat_database_process.database_model.owner.reference_projectuser
    if (database_owner.user.username == request.user.username or check_if_user_in_groups(request,['/be_paramount/app_ecoman/user-professional'])):
        if request.method == 'POST':
            form = EcoProcessEditForm(request.POST, instance=idemat_database_process)
        else:
            form = EcoProcessEditForm(request=request, instance=idemat_database_process)
            tuple_to_delete = form.fields['accessibility'].widget.choices[2]
            form.fields['accessibility'].widget.choices.remove(tuple_to_delete)
            tuple_to_delete = form.fields['accessibility'].widget.choices[2]
            form.fields['accessibility'].widget.choices.remove(tuple_to_delete)
        return lca_process_save_form(request, form, 'modals/lca_process/lca_process_update_modal.html')
    else:
        from EcoMan.forms import LcaProcessReviewForm
        if request.method == 'POST':
            form = LcaProcessReviewForm(request.POST, instance=idemat_database_process)
        else:
            form = LcaProcessReviewForm(request=request, instance=idemat_database_process)
        return lca_process_save_form(request, form, 'modals/lca_process/lca_process_review_modal.html')            


def lca_process_review(request, pk):
    idemat_database_process = get_object_or_404(Lca_Database_Process, pk=pk)
    from EcoMan.forms import LcaProcessReviewForm
    if request.method == 'POST':
        form = LcaProcessReviewForm(request.POST, instance=idemat_database_process)
    else:
        form = LcaProcessReviewForm(request=request, instance=idemat_database_process)
    return lca_process_save_form(request, form, 'modals/lca_process/lca_process_review_modal.html')

def lca_process_delete(request, pk):
    idemat_process = get_object_or_404(Lca_Database_Process, pk=pk)
    data = dict()
    context = dict()
    if request.method == 'POST':
        if  idemat_process.owner_id == request.user.projectuser.UUID or check_if_user_in_groups(request,['/be_paramount/app_ecoman/user-professional']):
            idemat_process.accessibility = 'ARCHIVE'
            idemat_process.save()
            data['form_is_valid'] = True  # This is just to play along with the existing code
    else:
        context['idemat_process'] = idemat_process
        data['html_form'] = render_to_string(   
                                                'modals/lca_process/lca_process_delete_modal.html',
                                                context,
                                                request=request,
                                            )
    return JsonResponse(data)

def lca_process_restore(request, pk):
    idemat_process = get_object_or_404(Lca_Database_Process, pk=pk)
    data = dict()
    context = dict()
    if request.method == 'POST':
        if  idemat_process.owner_id == request.user.projectuser.UUID or check_if_user_in_groups(request,['/be_paramount/app_ecoman/user-professional']):
            idemat_process.accessibility = "DATABASE_USERS"
            idemat_process.save()
            data['form_is_valid'] = True  # This is just to play along with the existing code
    else:
        context['idemat_process'] = idemat_process
        data['html_form'] = render_to_string(   
                                                'modals/lca_process/lca_process_restore_modal.html',
                                                context,
                                                request=request,
                                            )
    return JsonResponse(data)
#View used to reload dropdown list during addition of idemat process instance
def load_idemat_categories(request):


    category_id = request.GET['category_id']  #get id of selected category
    if category_id == "":
        category_id = 0


    group_id = request.GET['group_id']  #get id of selected category
    if group_id == "":
        group_id = 0

    group_query=Lca_Database_Group.objects.filter(category_model__id=category_id) #all groups under selected category_id
    subgroup_query=Lca_Database_Subgroup.objects.filter(group_model__id=group_id) 

    context={}
    context['group_model']=group_query
    context['subgroup_model']=subgroup_query 
    if category_id == 0: #User has selected nothing disable fields using javascript
        template_to_render ='modals/lca_process/process_group_dropdown_list_options.html'
    if category_id != 0 and group_id==0: #User has selected category reload group model 
        template_to_render ='modals/lca_process/process_group_dropdown_list_options.html'
    elif category_id != 0 and group_id!=0: #User has selected group reload subgroup list
        template_to_render ='modals/lca_process/process_subgroup_dropdown_list_options.html'

    return render(request, template_to_render, context)