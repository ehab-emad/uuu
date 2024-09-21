from django.views import generic
from django.shortcuts import  get_object_or_404
from BoltMan.models import *
from ConceptMan.models import *

from .modal import *


from MatMan.models import Engineering_Material

class EngineeringMaterialDetailView(generic.DetailView):
    model = Engineering_Material
    template_name = 'MatMan/materialdetail/materialdetail.html'

    def get_context_data(self, **kwargs):
        context = super(EngineeringMaterialDetailView, self).get_context_data(**kwargs)
        context['material'] = get_object_or_404(Engineering_Material, pk=self.kwargs['pk'])
        material = get_object_or_404(Engineering_Material, pk=self.kwargs['pk'])
        labels = ["GWP - Global Warming Potentian [kg CO² Equivalent]", "CED - [MJ]",  "ReCIPe 2016 Endpoint [pt]", "ReCIPe 2016 Human Health [DALY - Disability Adjusted Life Year]","RecIPe 2016 Eco Toxicity [Species.year - Local Secies loss per year]", "ReCIPe 2016  Resources [USD]",]
        data = [material.matgwp, material.matced, material.matrecipe_endp, material.matrecipe_hh, material.matrecipe_ecotox, material.matrecipe_reso]
        context['data']=data
        context['labels']=labels

        return context



    