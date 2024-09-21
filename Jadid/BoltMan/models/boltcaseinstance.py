from django.db import models
import uuid

class Bolt_Case_Instance(models.Model):
  UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=100,  default= 'DUMMY_BOLT_CASE_INSTANCE', editable=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  owner = models.ForeignKey("BoltMan.ProjectUser_BoltMan_Ref", models.SET_NULL, blank=True,null=True,)
  project_model=models.ForeignKey("BoltMan.Project_BoltMan_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a a project for assessment", default=None, blank=True,null=True, )

  logo = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Assessment Image")  
  vehicle=models.ManyToManyField("BoltMan.Vehicle_BoltMan_Ref",  help_text ="Select one or more vehicles for a Bolt Case Insance" )
  boltcase = models.ForeignKey("BoltMan.Bolt_Case", help_text="Select a position", on_delete=models.CASCADE, default=None)

  symmetric = models.BooleanField(verbose_name= "Symmetric", default=False)  

  
  from BoltMan.models.spatialposition import on_create_default_position
  spatial_position = models.OneToOneField("BoltMan.Spatial_Position", verbose_name="Spatial_Position", on_delete=models.CASCADE, help_text ="Position Vectors of the Instance", default = on_create_default_position ) 
  from BoltMan.models.boltrequirements import on_create_default_requirement
  requirements = models.OneToOneField("BoltMan.Bolt_Requirements", verbose_name="Spatial_Position", on_delete=models.CASCADE, help_text ="Requirements of the Instance", default = on_create_default_requirement ) 

  embedding = models.FloatField(editable=False, verbose_name= "Connection - Settling rate", default=None, blank=True, null=True)      #Setzbetrag D162

  description = models.CharField(max_length=1000,  default= 'DUMMY_BOLT_CASE_INSTANCE', editable=True, blank=True)
  DRAFT = 'Draft'
  TESTING = 'Testing'
  RELEASE = 'Release'
  MATURITY = [
    (DRAFT, ('Initial investigation')),
    (TESTING, ('Released for testing')),
    (RELEASE, ('Released for production')),
   ]
  status = models.CharField(choices=MATURITY, max_length=32, default=DRAFT)
  def __str__(self):
    return str(self.name)
  class Meta:
    app_label = 'BoltMan'


  def calculate_settling_rate(self):

    try:

        boltcase_temp_set = self.bolt_case_set.all()
        for object in boltcase_temp_set:
          boltcase_temp = object
        if self.meaf > self.mesf: #load type
          load_type = "tension/compression"
        else:
          load_type = "shear"


        #Embedding in thread D115
        settling_rate = self.embedding_vdi_guide.get(boltcase_temp.roughness, {}).get(load_type,[])[0]


        #Embedding under head D116
        if boltcase_temp.bolt_case_class == "Bolted Joint":   #Bolted Joint
          settling_rate = settling_rate + self.embedding_vdi_guide.get(boltcase_temp.roughness, {}).get(load_type,[])[1] * 2

        if boltcase_temp.bolt_case_class == "Tapped Thread Joint":  #Tapped Thread Joint
          settling_rate = settling_rate + self.embedding_vdi_guide.get(boltcase_temp.roughness, {}).get(load_type,[])[1] * 1

        #Embedding at interfaces
        if boltcase_temp.washer_head: 
          number_of_washers = 1
        if boltcase_temp.washer_nut: 
          number_of_washers = number_of_washers + 1
        settling_rate = settling_rate + self.embedding_vdi_guide.get(boltcase_temp.roughness, {}).get(load_type,[])[2] * (boltcase_temp.nop -1 + number_of_washers)

        self.embedding = settling_rate/1000

        embedding_vdi_guide={ 
        "RL": {"tension/compression": [3, 2.5, 1.5], "shear": [3, 3, 2]},
        "RM": {"tension/compression": [3, 3, 2], "shear": [3, 4.5, 2.5]},
        "RH": {"tension/compression": [3, 4, 3], "shear": [3, 6.5, 3.5]},
         }
    except (TypeError, AttributeError):
        print('Boltcase not fully defined!')

