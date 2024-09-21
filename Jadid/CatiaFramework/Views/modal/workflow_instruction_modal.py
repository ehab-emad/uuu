from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from CatiaFramework.models import Workflow_Instruction

#qlca-----------------------------------------------------------------------------------
def instruction_save_form(request, form, template_name, uuid_instruction = None):
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            instruction = form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    context.update({'uuid_instruction':uuid_instruction})
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def workflow_instruction_create_modal(request, uuid_workflow = None):
    '''not utilised'''
    from CatiaFramework.forms import InstructionForm
    if request.method == 'POST':
        form = InstructionForm(request.POST, request.FILES)
    else:
        form = InstructionForm()
    return instruction_save_form(request, form, 'modals/workflow_instruction/instruction_create_modal.html', uuid_workflow)



def workflow_instruction_update_modal(request, uuid_instruction):

    instruction = get_object_or_404(Workflow_Instruction, pk=uuid_instruction)
    from CatiaFramework.forms import InstructionForm
    if request.method == 'POST':
        form = InstructionForm(request.POST, request.FILES, instance=instruction)
    else:
        form = InstructionForm(instance=instruction)
    return instruction_save_form(request, form, 'modals/workflow_instruction/instruction_update_modal.html')

def workflow_instruction_delete_modal(request, uuid_instruction):
    '''not utilised'''
    instruction = get_object_or_404(Workflow_Instruction, pk=uuid_instruction)
    data = dict()
    if request.method == 'POST':
        instruction.part_model.delete()
        instruction.delete()
        data['form_is_valid'] = True 
    else:
        context = {'instruction': instruction}
        data['html_form'] = render_to_string('modals/workflow_instruction/instruction_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)

