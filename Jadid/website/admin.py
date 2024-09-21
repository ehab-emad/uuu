from django.contrib import admin
from django.contrib import auth

from .models import Project
from website.models import ProjectUser
from website.models import Room
from website.models import Energy_Source
from website.models import Vehicle
from website.models import Organisation
from ConceptMan.models.part import Part
from ConceptMan.models.concept import Concept
from ConceptMan.models.manufacturing_process import Manufacturing_Process
from website.models.production_rate import Production_Rate
from website.models.production_rate import Production_Rate


from EcoMan.models.analysis_comparison import Analysis_Comparison
from EcoMan.models.analysis_settings import Analysis_Settings
from EcoMan.models.analysis import Analysis
from EcoMan.models import Lca_Database
from EcoMan.models import Lca_Database_Process
from EcoMan.models import Lca_Part
from EcoMan.models import Instance_Idemat_Database_Process
from EcoMan.models import Utilisation_Process
from EcoMan.models import Lca_Database_Category
from EcoMan.models import Lca_Database_Group
from EcoMan.models import Lca_Database_Subgroup
from EcoMan.models import Instance_Idemat_Database_Process
from EcoMan.models import Utilisation_Process

from EcoMan.models import Lca_Property
from EcoMan.models import Lca_Support_Ticket

from MatMan.models.engineering_material import Engineering_Material

from BoltMan.models.boltcase import Bolt_Case
from BoltMan.models.boltcaseinstance import Bolt_Case_Instance
from BoltMan.models.boltgeometry import Bolt_Geometry
from BoltMan.models.spatialposition import Spatial_Position
from BoltMan.models.partmaterial import Part_Material
from BoltMan.models.boltmaterial import Bolt_Material
from BoltMan.models.frictionthread import Friction_Thread
from BoltMan.models.frictionhead import Friction_Head
from BoltMan.models.frictionjoint import Friction_Joint
from BoltMan.models.washer import Washer
from BoltMan.models.metricthread import Metric_Thread

from website.models.token import Token

admin.site.register(Token)

admin.site.register(Organisation)
admin.site.register(Project)
admin.site.register(ProjectUser)
admin.site.register(Room)
admin.site.register(Engineering_Material)

admin.site.register(Vehicle)
admin.site.register(Concept)
admin.site.register(Manufacturing_Process)
admin.site.register(Production_Rate)

admin.site.register(Bolt_Case)
admin.site.register(Bolt_Case_Instance)
admin.site.register(Bolt_Geometry)
admin.site.register(Spatial_Position)
admin.site.register(Part)
admin.site.register(Part_Material)
admin.site.register(Bolt_Material)
admin.site.register(Friction_Thread)
admin.site.register(Friction_Head)
admin.site.register(Friction_Joint)
admin.site.register(Washer)
admin.site.register(Metric_Thread)


admin.site.register(Analysis)
admin.site.register(Analysis_Comparison)
admin.site.register(Analysis_Settings)
admin.site.register(Lca_Database)
admin.site.register(Lca_Database_Process)
admin.site.register(Instance_Idemat_Database_Process)
admin.site.register(Energy_Source)
admin.site.register(Lca_Property)
admin.site.register(Lca_Part)
admin.site.register(Utilisation_Process)
admin.site.register(Lca_Support_Ticket)

admin.site.register(Lca_Database_Category)
admin.site.register(Lca_Database_Group)
admin.site.register(Lca_Database_Subgroup)


