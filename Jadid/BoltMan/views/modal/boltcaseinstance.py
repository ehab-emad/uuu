from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ...models import Bolt_Case
from ...models import Bolt_Case_Instance
from ...forms.forms import BoltCaseInstanceFormCreate, BoltCaseInstanceForm
from django.urls import reverse
#Boltcase-----------------------------------------------------------------------------------
def boltcaseinstance_save_form(request, form, template_name,  redirect = False):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            newobject=form.save()
            data['form_is_valid'] = True
            data['pk'] =newobject.id
            data['address'] =reverse('assessment_detail_view', newobject.id)
        else:
            data['form_is_valid'] = False

    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),

    return JsonResponse(data)

def boltcaseinstance_create(request):
    if request.method == 'POST':
        form = BoltCaseInstanceFormCreate(request.POST)
    else:
        form = BoltCaseInstanceFormCreate()
    return boltcaseinstance_save_form(request, form, 'modals/boltcaseinstance/boltcaseinstance_create_modal.html')

def boltcaseinstance_update(request, pk):
    car = get_object_or_404(Bolt_Case_Instance, pk=pk)
    if request.method == 'POST':
        form = BoltCaseInstanceFormCreate(request.POST, instance=car)
         
    else:
        form = BoltCaseInstanceFormCreate(instance=car)
    return boltcaseinstance_save_form(request, form, 'modals/boltcaseinstance/boltcaseinstance_update_modal.html')

def boltcaseinstance_delete(request, pk):
    boltcaseinstance = get_object_or_404(Bolt_Case_Instance, pk=pk)
    data = dict()
    if request.method == 'POST':
        boltcaseinstance.delete()
        data['form_is_valid'] = True  
    else:
        context = {'boltcaseinstance': boltcaseinstance}
        data['html_form'] = render_to_string('modals/boltcaseinstance/boltcaseinstance_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)

