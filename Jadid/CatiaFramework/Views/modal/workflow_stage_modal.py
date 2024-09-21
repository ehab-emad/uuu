from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from CatiaFramework.models import Workflow_Stage, Workflow, Workflow_Instruction, ProjectUser_CatiaFramework_Ref, Project_CatiaFramework_Ref

#qlca-----------------------------------------------------------------------------------
def stage_save_form(request, form, template_name, uuid_workflow = None):
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            stage = form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    context.update({'uuid_workflow':uuid_workflow})
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def workflow_stage_create_modal(request, uuid_workflow = None):

    from CatiaFramework.forms import StageForm
    if request.method == 'POST':
            parent_workflow = get_object_or_404(Workflow, pk=uuid_workflow)

            #find root stage of the workflow
            root_stages = parent_workflow.get_root_stages()
            root_stage = None if not root_stages else root_stages.get()

            #find the last stage in the workflow
            last_stage = None if not root_stage else root_stage.get_last_stage()

            form = StageForm(request.POST, request.FILES)
            form.instance.owner =  ProjectUser_CatiaFramework_Ref.objects.filter(UUID = request.user.projectuser.UUID).get()   
            form.instance.project_model = Project_CatiaFramework_Ref.objects.filter(UUID = request.user.projectuser.current_project.UUID).get()
            form.instance.type = "TEMPLATE"
            form.instance.status = "WAITING"  
            form.instance.parent_stage = last_stage
            form.instance.parent_workflow = parent_workflow
            form.instance.instrucion = Workflow_Instruction.objects.create()
            form.instance.is_active = False

    else:
        form = StageForm()
    return stage_save_form(request, form, 'modals/workflow_stage/stage_create_modal.html', uuid_workflow)



def workflow_stage_update_modal(request, uuid_stage):

    stage = get_object_or_404(Workflow_Stage, pk=uuid_stage)
    from CatiaFramework.forms import StageForm
    if request.method == 'POST':
        form = StageForm(request.POST, request.FILES, instance=stage)
    else:
        form = StageForm(instance=stage)
    return stage_save_form(request, form, 'modals/workflow_stage/stage_update_modal.html')

def workflow_stage_delete_modal(request, uuid_stage):
    data = dict()
    stage = get_object_or_404(Workflow_Stage, pk=uuid_stage)
    if request.method == 'POST':

        stage_parent = stage.parent_stage
        stage_children = Workflow_Stage.objects.filter( parent_stage = stage)
        if stage_children:
            stage_children=stage_children.get()
        if stage_parent == None: #when usere deletes a root stage of the workflow
             stage_children.parent_workfow = stage.parent_workflow
             stage_children.save()
        if stage_children:
            stage_children.parent_stage = stage_parent
            stage_children.save()
        stage.delete()
        data['form_is_valid'] = True 
    else:
        context = {'stage': stage}
        data['html_form'] = render_to_string('modals/workflow_stage/stage_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)