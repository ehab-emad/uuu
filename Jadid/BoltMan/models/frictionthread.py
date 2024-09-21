from django.db import models
import uuid


class Friction_Thread(models.Model):
  UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  owner = models.ForeignKey("BoltMan.ProjectUser_BoltMan_Ref", models.SET_NULL, blank=True,null=True,)
  PRECISION_CHOICES = (
      ("NP", "Non-precision"),
      ("P", "Precision"),

  )

  CLASS_CHOICES = (
      ("CLASS_A", "Class A"),
      ("CLASS_B", "Class B"),
      ("CLASS_C", "Class C"),
      ("CLASS_D", "Class D"),
      ("CLASS_E", "Class E"),
      ("SC1", "SC1"),
      ("SC2", "SC2"),
      ("SC3", "SC3"),
      ("SC4", "SC4"),
      ("SC5", "SC5"),    
      ("SC6", "SC6"), 
      ("SC7", "SC7"),    
      ("SC8", "SC8"),  
      ("BC1", "BC1"),    
      ("BC2", "BC2"), 
      ("BC3", "BC3"),    
      ("BC4", "BC4"), 
      ("BC5", "BC5"),    
      ("NC", "Not Classified"),             
  )

  f_class = models.CharField(max_length=100, choices=CLASS_CHOICES, verbose_name= "Class", editable=True, default= None)
  colour = models.CharField(max_length=100, verbose_name= "Colour", editable=True, default= None)
  surface = models.CharField(max_length=100, verbose_name= "Surface", editable=True, default= None)
  precision = models.CharField(max_length=30, choices=PRECISION_CHOICES, verbose_name= "Precision",  editable=True, default= PRECISION_CHOICES[0])
  lubrication = models.CharField(max_length=500, verbose_name= "Lubrication", editable=True, default= None)
  friction_av=models.FloatField(editable=True, verbose_name= "Avarage friction", default= None)
  friction_min=models.FloatField(editable=True, verbose_name= "Minimum friction", default= None)
  friction_max=models.FloatField(editable=True, verbose_name= "Maximum friction", default= None)
  source = models.CharField(max_length=100, verbose_name= "Source", editable=True, default= None)
  notes = models.CharField(max_length=500, verbose_name= "Notes", editable=True, default= None)
  class Meta:
    app_label = 'BoltMan'
  def __str__(self):
    return 'CLASS: ' +str(self.f_class) + ',' + str(self.surface) + ' | Colour:' +  str(self.colour) + ' | Colour:' +  str(self.surface) + '|Friciton av:' + str(self.friction_av) + '|Lubrication:' + str(self.lubrication)