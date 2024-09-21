from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from MatMan.models import Engineering_Material
from ConceptMan.models import Concept

class ConceptDetailView_Part(TemplateView):
    template_name = 'ConceptMan/concept/conceptdetail_part.html'
    def get_context_data(self, **kwargs):
        context = super(ConceptDetailView_Part, self).get_context_data(**kwargs)
        context['concept'] = get_object_or_404(Concept, pk=self.kwargs['pk'])
        concept = Concept.objects.get(pk=self.kwargs['pk'])
        parts_in_use =concept.parts.all()
        context['objects'] = parts_in_use
        labels = []
        data = []
        for part in parts_in_use:
            labels.append(part.name)
            data.append(part.weight)
        context['data']=data
        context['labels']=labels
        return context

class ConceptDetailView_Bolt_Case(TemplateView):
    template_name = 'ConceptMan/concept/conceptdetail_boltcase.html'
    def get_context_data(self, **kwargs):
        context = super(ConceptDetailView_Bolt_Case, self).get_context_data(**kwargs)
        context['concept'] = get_object_or_404(Concept, pk=self.kwargs['pk'])
        concept = Concept.objects.get(pk=self.kwargs['pk'])
        parts_in_use =concept.parts.all()
        context['objects'] = parts_in_use
        return context


class ConceptDetailView_Engineering_Material(TemplateView):
    template_name = 'ConceptMan/concept/conceptdetail_material.html'
    def get_context_data(self, **kwargs):
        context = super(ConceptDetailView_Engineering_Material, self).get_context_data(**kwargs)
        context['concept'] = get_object_or_404(Concept, pk=self.kwargs['pk'])
        concept = Concept.objects.get(pk=self.kwargs['pk'])
        parts_in_use =concept.parts.all()
        materials_in_use = []
        for part in parts_in_use:
            materials_in_use.append(part.engineering_material)

        materials_in_use = list( dict.fromkeys(materials_in_use) )

        context["objects"] = Engineering_Material.objects.filter(id__in=[emp.id for emp in materials_in_use])
        labels = []
        data = []
        for material in materials_in_use:
            labels.append(material.name)
            data.append(0)
        x=0

        for material in materials_in_use:
            for part in parts_in_use:
                if part.engineering_material.id == material.id:
                   data[x]=data[x]+part.weight
            x=x+1
        context['data']=data
        context['labels']=labels
        return context


