from django.shortcuts import render

# Create your views here.

from .views import *

from django.views import generic
from django.views.generic import View, TemplateView
from MatMan.models import Engineering_Material

class index(TemplateView):
    template_name = 'MatMan/index_materialgroups.html'

class index_metals(TemplateView):
    template_name = 'MatMan/index_metals.html'





class MetalFerrousListView(TemplateView):
    template_name = 'MatMan/list_metalferrous.html'
    def get_context_data(self, **kwargs):
        context = super(MetalFerrousListView, self).get_context_data(**kwargs)
        context['objects'] = Engineering_Material.objects.all().filter(materialgroup="Metals Ferrous")
        return context

class MetalNonFerrousListView(TemplateView):
    template_name = 'MatMan/list_metalnonferrous.html'
    def get_context_data(self, **kwargs):
        context = super(MetalNonFerrousListView, self).get_context_data(**kwargs)
        context['objects'] = Engineering_Material.objects.all().filter(materialgroup="Metals Non-Ferrous")
        return context

class PlasticListView(TemplateView):
    template_name = 'MatMan/list_plastic.html'
    def get_context_data(self, **kwargs):
        context = super(PlasticListView, self).get_context_data(**kwargs)
        context['objects'] = Engineering_Material.objects.all().filter(materialgroup="Plastic")
        return context

class CeramicListView(TemplateView):
    template_name = 'MatMan/list_ceramic.html'
    def get_context_data(self, **kwargs):
        context = super(CeramicListView, self).get_context_data(**kwargs)
        context['objects'] = Engineering_Material.objects.all().filter(materialgroup="Ceramic")
        return context

class CompositeListView(TemplateView):
    template_name = 'MatMan/list_composite.html'
    def get_context_data(self, **kwargs):
        context = super(CompositeListView, self).get_context_data(**kwargs)
        context['objects'] = Engineering_Material.objects.all().filter(materialgroup="Composite")
        return context

class SpecialListView(TemplateView):
    template_name = 'MatMan/list_special.html'
    def get_context_data(self, **kwargs):
        context = super(SpecialListView, self).get_context_data(**kwargs)
        context['objects'] = Engineering_Material.objects.all().filter(materialgroup="Special")
        return context
