from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ...models import Bolt_Case
from ...forms.forms import BoltCaseFormCreate

#Boltcase-----------------------------------------------------------------------------------
def boltcase_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            newobject=form.save()
            data['form_is_valid'] = True
            data['address'] =reverse('assessment_detail_view-detailview', newobject.UUID)
        else:
            data['form_is_valid'] = False

    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),

    return JsonResponse(data)

def boltcase_create(request):
    if request.method == 'POST':
        form = BoltCaseFormCreate(request.POST)
    else:
        form = BoltCaseFormCreate()
    return boltcase_save_form(request, form, 'modals/boltcase/boltcase_create_modal.html')

def boltcase_update(request, pk):
    car = get_object_or_404(Bolt_Case, pk=pk)
    if request.method == 'POST':
        form = BoltCaseFormCreate(request.POST, instance=car)
        car.set_vdi_input_param()
        car.resilience_bolt()
        car.resilience_parts_same_Emodulus()   
        car.resilience_parts_different_Emodulus()           
    else:
        form = BoltCaseFormCreate(instance=car)
    return boltcase_save_form(request, form, 'modals/boltcase/boltcase_update_modal.html')

def boltcase_delete(request, pk):
    boltcase = get_object_or_404(Bolt_Case, pk=pk)
    data = dict()
    if request.method == 'POST':
        boltcase.delete()
        data['form_is_valid'] = True  
    else:
        context = {'boltcase': boltcase}
        data['html_form'] = render_to_string('modals/boltcase/boltcase_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)


def select_friction_head_modal(request, uuid_boltcase_instance):
    boltcase = get_object_or_404(Bolt_Case, UUID=uuid_boltcase_instance)
    from BoltMan.forms import BoltcaseSelectFrictionHeadForm
    if request.method == 'POST':
        form = BoltcaseSelectFrictionHeadForm(request.POST, instance = boltcase)
    else:
        form = BoltcaseSelectFrictionHeadForm(instance = boltcase)
    return boltcase_save_form(request, form, 'modals/boltcase/boltcase_select_friction_head_modal.html')

def select_friction_joint_modal(request, uuid_boltcase_instance):
    boltcase = get_object_or_404(Bolt_Case, UUID=uuid_boltcase_instance)
    from BoltMan.forms import BoltcaseSelectFrictionJointForm
    if request.method == 'POST':
        form = BoltcaseSelectFrictionJointForm(request.POST, instance = boltcase)
    else:
        form = BoltcaseSelectFrictionJointForm(instance = boltcase)
    return boltcase_save_form(request, form, 'modals/boltcase/boltcase_select_friction_joint_modal.html')

def select_friction_thread_modal(request, uuid_boltcase_instance):
    boltcase = get_object_or_404(Bolt_Case, UUID=uuid_boltcase_instance)
    from BoltMan.forms import BoltcaseSelectFrictionThreadForm
    if request.method == 'POST':
        form = BoltcaseSelectFrictionThreadForm(request.POST, instance = boltcase)
    else:
        form = BoltcaseSelectFrictionThreadForm(instance = boltcase)
    return boltcase_save_form(request, form, 'modals/boltcase/boltcase_select_friction_thread_modal.html')