from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ...models import Bolt_Case, Bolted_Part,  Vehicle_BoltMan_Ref, ProjectUser_BoltMan_Ref, Project_BoltMan_Ref
from ...models import Bolt_Case_Instance
from ...forms.forms import BoltCaseInstanceFormCreate, BoltCaseInstanceForm
from django.urls import reverse
#Boltcase-----------------------------------------------------------------------------------
def single_assessment_save_form(request, form, template_name,  redirect = False):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():


            #for single assessment we want to achieve forms similar to those in excel list so default objects will be created automatically user can replace them later on if necessary
            new_boltcase = Bolt_Case.objects.create()
            from BoltMan.models import Bolt_Geometry
            new_boltcase.bolt_geometry = Bolt_Geometry.objects.create()
            from BoltMan.models import Washer
            new_boltcase.washer_head =  Washer.objects.create()  
            new_boltcase.washer_nut =  Washer.objects.create()

            new_boltcase.part_1 =  Bolted_Part.objects.create()
            new_boltcase.part_2 =  Bolted_Part.objects.create()
            new_boltcase.part_3 =  Bolted_Part.objects.create()

            new_boltcase.save()

            form.cleaned_data['boltcase'] = new_boltcase
            form.instance.boltcase = form.cleaned_data['boltcase']
            newobject=form.save()

            #currently only sandbox project and sandbox vehicle will be accepted
            UUID_current_project = request.user.projectuser.current_project.UUID
            UUID_current_user = request.user.projectuser.UUID


            newobject.project_model = get_object_or_404(Project_BoltMan_Ref, UUID = UUID_current_project) 
            newobject.owner = get_object_or_404(ProjectUser_BoltMan_Ref, UUID = UUID_current_user)
            newobject.save()


            data['form_is_valid'] = True
            data['pk'] =newobject.UUID
            data['redirect'] =True
            data['redirect_address'] =reverse('BoltMan:assessment_detail_view', args=[str(newobject.UUID)])
        else:
            data['form_is_valid'] = False

    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),

    return JsonResponse(data)

def single_assessment_create(request):

    if request.method == 'POST':

        form = BoltCaseInstanceForm(request.POST, request.FILES)
    else:

        form = BoltCaseInstanceForm()


    return single_assessment_save_form(request, form, 'modals/singleassessment/single_assessment_create_modal.html', redirect=True) #redirect site in analysis.js

def boltcaseinstance_update(request, pk):
    car = get_object_or_404(Bolt_Case_Instance, pk=pk)
    if request.method == 'POST':
        form = BoltCaseInstanceFormCreate(request.POST, instance=car)
         
    else:
        form = BoltCaseInstanceFormCreate(instance=car)
    return single_assessment_save_form(request, form, 'modals/singleassessment/single_assessment_update_modal.html')

def single_assessment_delete(request, pk):
    boltcaseinstance = get_object_or_404(Bolt_Case_Instance, pk=pk)
    data = dict()
    if request.method == 'POST':
        boltcaseinstance.delete()
        data['form_is_valid'] = True  
    else:
        context = {'boltcaseinstance': boltcaseinstance}
        data['html_form'] = render_to_string('modals/singleassessment/single_assessment_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)




