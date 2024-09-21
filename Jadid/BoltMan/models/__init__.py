from  BoltMan.models.boltcase import Bolt_Case
from  BoltMan.models.boltcaseinstance import Bolt_Case_Instance
from  BoltMan.models.spatialposition import Spatial_Position
from  BoltMan.models.boltrequirements import Bolt_Requirements
from  BoltMan.models.boltgeometry import Bolt_Geometry
from  BoltMan.models.partmaterial import Part_Material

from  BoltMan.models.metricthread import Metric_Thread
from  BoltMan.models.partmaterial import Part_Material
from  BoltMan.models.frictionhead import Friction_Head
from  BoltMan.models.frictionthread import Friction_Thread
from  BoltMan.models.frictionjoint import Friction_Joint
from  BoltMan.models.washer import Washer
from  BoltMan.models.bolted_part import Bolted_Part
from  BoltMan.models.boltmaterial import Bolt_Material

from  BoltMan.models.vehicle_boltman_ref import Vehicle_BoltMan_Ref
from  BoltMan.models.projectuser_boltman_ref import ProjectUser_BoltMan_Ref
from  BoltMan.models.project_boltman_ref import Project_BoltMan_Ref

class Meta:
    managed = True
    db_table = 'table_name'

