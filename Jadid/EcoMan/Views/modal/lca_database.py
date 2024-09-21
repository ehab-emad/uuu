from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from EcoMan.models import Lca_Database, Lca_Database_Process, ProjectUser_EcoMan_Ref, Project_EcoMan_Ref
from EcoMan.scripts import *
from website.scripts import *
from website.security import check_if_user_in_groups
def lca_db_save_form(request, form, template_name, redirect = False, import_processes = True):
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            lca_db =form.save()
            lca_db.owner=get_object_or_404(ProjectUser_EcoMan_Ref, UUID=request.user.projectuser.UUID)
            lca_db.save()
            if(form.cleaned_data.get('logo')):
                lca_db.logo = form.cleaned_data.get('logo')
                lca_db.save()
            data['redirect'] = redirect
            data['pk'] =lca_db.pk
            data['form_is_valid'] = True
            if lca_db.accessibility == "ORGANISATION":
                organisation_project = Project.objects.filter(name = "Organisation_LCA_Project").get()
                lca_db.projects.add(Project_EcoMan_Ref.objects.filter(UUID = organisation_project.UUID).get())
            if lca_db.accessibility == "PROJECT":
                current_project = request.user.projectuser.current_project
                lca_db.projects.add(Project_EcoMan_Ref.objects.filter(UUID = current_project.UUID).get())            
            lca_db.save()
            #if file uploaded try to import processes from self.last_import_document as parameter not provided
            if import_processes:
                if request.FILES.get('last_import_document'):
                    lca_db.LCADatabaseFileImport()
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

def lca_db_create(request):
    from EcoMan.forms import LcaDBForm
    if request.method == 'POST':
        form = LcaDBForm(request.POST, files=request.FILES, request = request)
    else:
        form = LcaDBForm(request = request,)
        if check_if_user_in_groups(request, ['/be_paramount/app-ecoman/user-professional']) == False:   #use which is not is_staff can only add project releated databases 
            new_list = [tup for tup in form.fields['accessibility'].widget.choices if tup[0] != 'ORGANISATION' and tup[0] != 'OPEN']
            form.fields['accessibility'].widget.choices = new_list                
    return lca_db_save_form(request, form, 'modals/lca_db/lca_db_create_modal.html', redirect=False)

def lca_db_create_and_edit(request):
    from EcoMan.forms import LcaDBForm
    if request.method == 'POST':
        form = LcaDBForm(request.POST)
    else:
        form = LcaDBForm(request = request,)

    return lca_db_save_form(request, form, 'modals/lca_db/lca_db_create_modal.html', redirect=True)

def lca_db_update(request, pk):
    qlca = get_object_or_404(Lca_Database, pk=pk)
    from EcoMan.forms import LcaDBForm_update
    if request.method == 'POST':
        form = LcaDBForm_update(request.POST, instance=qlca)
    else:
        form = LcaDBForm_update(request = request, instance=qlca)
    return lca_db_save_form(request, form, 'modals/lca_db/lca_db_update_modal.html', import_processes = False)

def lca_db_import_excel(request, pk):
    qlca = get_object_or_404(Lca_Database, pk=pk)
    from EcoMan.forms import LcaDBImportExcelForm
    if request.method == 'POST':
        form = LcaDBImportExcelForm(request.POST, files=request.FILES, instance=qlca, )
    else:
        form = LcaDBImportExcelForm(request = request, instance=qlca)
    return lca_db_save_form(request, form, 'modals/lca_db/lca_db_import_excel_modal.html')

def lca_db_delete(request, pk):
    eco_db = get_object_or_404(Lca_Database, pk=pk)
    data = dict()
    if request.method == 'POST':
        if  eco_db.owner_id == request.user.projectuser.UUID:
            eco_db.is_archive = True
            eco_db.save()
            query = Lca_Database_Process.objects.filter(database_model = eco_db)
            for object in query:
                object.accessibility = "ARCHIVE"
                object.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False

    else:
        context = {'eco_db': eco_db}
        data['html_form'] = render_to_string('modals/lca_db/lca_db_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)

def lca_db_restore(request, pk):
    eco_db = get_object_or_404(Lca_Database, pk=pk)
    data = dict()
    if request.method == 'POST':
        if  eco_db.owner_id == request.user.projectuser.UUID:
            eco_db.is_archive = False
            eco_db.save()
            query = Lca_Database_Process.objects.filter(database_model = eco_db)
            for object in query:
                object.accessibility = "DATABASE_USERS"
                object.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        context = {'eco_db': eco_db}
        data['html_form'] = render_to_string('modals/lca_db/lca_db_restore_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)
