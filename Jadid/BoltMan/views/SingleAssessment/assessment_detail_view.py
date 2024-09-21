import json
from django.shortcuts import  get_object_or_404, redirect
from django.views import generic
from EcoMan.models import Analysis
from BoltMan.models import Bolt_Case_Instance
from django.http import HttpResponseRedirect
from EcoMan.QLCA_Idemat_Calculation import * 
from website.scripts import *
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

def continue_assessment_detail_view(request):   #this view has to be corrected for analysis objects
    '''User will be redirected to the last edited Analysis Comparison  
    '''

    obj= Bolt_Case_Instance.objects.filter(owner__UUID=str(request.user.projectuser.UUID))
    try:
        obj=obj.latest('updated_at')
    except:
        return  redirect('BoltMan:assessment_welcome_screen')
    url = reverse('BoltMan:assessment_detail_view', kwargs={'pk': obj.id})
    return HttpResponseRedirect(url)

class assessment_detail_view(generic.DetailView):
    model = Bolt_Case_Instance
    template_name = 'BoltMan/SingleAssessment/assessment_detail_view.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated: #force user to login
            return HttpResponseRedirect('/user/login')
        #check if user has rights to see assessment
        analysis_project_UUID = Bolt_Case_Instance.objects.filter(UUID = kwargs['uuid']).get().project_model.UUID
        projects = request.user.projectuser.authorised_projects.all()
        for project in projects:
            if project.UUID == analysis_project_UUID: 
                return super().dispatch(request, *args, **kwargs)
        return HttpResponseRedirect('index')
        

    def get_object(self):
        
        if 'uuid' in self.kwargs:
            peka=str(self.kwargs.get('uuid'))
            return get_object_or_404(Bolt_Case_Instance, UUID=peka) 

        obj= Analysis.objects.filter(owner_id=self.request.user.id)
        #obj=obj.filter(playground=True) should be single_assessment
        obj=obj.latest('updated_at')

        if not obj:
            return redirect('assessment_welcome_screen')
        else:
            single_assessment = get_object_or_404(Bolt_Case_Instance, pk=str(obj.UUID))  
            return  single_assessment

        
    def get_context_data(self, **kwargs):      
        context = super().get_context_data(**kwargs)
   
        #get spatial_position form
        from BoltMan.forms import PositionForm
        form_spatial_position = PositionForm(instance=self.object.spatial_position)
        context['form_spatial_position'] = form_spatial_position

        #get bolt geometry form
        from BoltMan.forms import SingleassessmentBoltcaseBoltgeometryForm
        form_boltgeometry = SingleassessmentBoltcaseBoltgeometryForm(instance=self.object.boltcase.bolt_geometry)
        context['form_boltgeometry'] = form_boltgeometry

        #get requirements form
        from BoltMan.forms import RequirementsForm
        form_requirements = RequirementsForm(instance=self.object.requirements)
        context['form_requirements'] = form_requirements

        #get bolt material form
        from BoltMan.forms import BoltMaterialForm
        form_boltmaterial = BoltMaterialForm(instance=self.object.boltcase.bolt_geometry.material)
        context['form_boltmaterial'] = form_boltmaterial

        #get washer head form
        from BoltMan.forms import SingleassessmentWasherForm
        form_washer_head = SingleassessmentWasherForm(instance=self.object.boltcase.washer_head)
        context['form_washer_head'] = form_washer_head

        #get washer nut form
        from BoltMan.forms import SingleassessmentWasherForm
        form_washer_nut = SingleassessmentWasherForm(instance=self.object.boltcase.washer_nut)
        context['form_washer_nut'] = form_washer_nut

        #get friction head form
        from BoltMan.forms import SingleassessmentFrictionHeadForm
        form_friction_head = SingleassessmentFrictionHeadForm(instance=self.object.boltcase.friction_head)
        context['form_friction_head'] = form_friction_head

        #get friction joint form
        from BoltMan.forms import SingleassessmentFrictionJointForm
        form_friction_joint = SingleassessmentFrictionJointForm(instance=self.object.boltcase.friction_joint)
        context['form_friction_joint'] = form_friction_joint

        #get friction thread form
        from BoltMan.forms import SingleassessmentFrictionThreadForm
        form_friction_thread = SingleassessmentFrictionThreadForm(instance=self.object.boltcase.friction_thread)
        context['form_friction_thread'] = form_friction_thread

        #get part_1
        from BoltMan.forms import SingleassessmentPartForm
        form_part_1 = SingleassessmentPartForm(instance=self.object.boltcase.part_1)
        context['form_part_1'] = form_part_1

        #get part_2
        from BoltMan.forms import SingleassessmentPartForm
        form_part_2 = SingleassessmentPartForm(instance=self.object.boltcase.part_2)
        context['form_part_2'] = form_part_2

        #get part_3
        from BoltMan.forms import SingleassessmentPartForm
        form_part_3 = SingleassessmentPartForm(instance=self.object.boltcase.part_3)
        context['form_part_3'] = form_part_3        

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')
        if action == 'spatial_position_update':
            instance = self.object.spatial_position
            from BoltMan.forms import PositionForm
            form = PositionForm(request.POST, instance= instance)
            if form.is_valid():
                form.save()
        if action == 'requirements_update':
            instance = self.object.boltcase.requirements
            from BoltMan.forms import RequirementsForm
            form = RequirementsForm(request.POST, instance= instance)
            if form.is_valid():
                form.save()

        if action == 'bolt_geometry_update':
            instance = self.object.boltcase.bolt_geometry
            from BoltMan.forms import SingleassessmentBoltcaseBoltgeometryForm
            form = SingleassessmentBoltcaseBoltgeometryForm(request.POST, instance= instance)
            if form.is_valid():
                form.save()

        if action == 'washer_nut_update':
            instance = self.object.boltcase.washer_nut
            from BoltMan.forms import SingleassessmentWasherForm
            form = SingleassessmentWasherForm(request.POST, instance= instance)
            if form.is_valid():
                form.save()
        if action == 'washer_head_update':
            instance = self.object.boltcase.washer_head
            from BoltMan.forms import SingleassessmentWasherForm
            form = SingleassessmentWasherForm(request.POST, instance= instance)
            if form.is_valid():
                form.save()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)