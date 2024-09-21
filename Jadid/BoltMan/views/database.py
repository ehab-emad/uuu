from BoltMan.models.boltmaterial import Bolt_Material
from django.views import generic
from ..models import Part_Material,  Friction_Head, Friction_Thread

#DB-----------------------------------------------------------------------------------
class PartMaterialListView(generic.ListView):
    template_name = 'BoltMan/VariablesDatabase/db_partmaterialindex.html'
    def get_queryset(self):
        return Part_Material.objects.all()

class BoltMaterialListView(generic.ListView):
    template_name = 'BoltMan/VariablesDatabase/db_boltmaterialindex.html'
    def get_queryset(self):
        return Bolt_Material.objects.all()    

class FrictionHeadListView(generic.ListView):
    template_name = 'BoltMan/VariablesDatabase/db_frictionheadindex.html'
    def get_queryset(self):
        return Friction_Head.objects.all()    

class FrictionThreadListView(generic.ListView):
    template_name = 'BoltMan/VariablesDatabase/db_frictionthreadindex.html'

    def get_queryset(self):
        return Friction_Thread.objects.all()  
#-----------------------------------------------------------------------------------
