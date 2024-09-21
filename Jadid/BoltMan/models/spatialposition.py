from django.db import models
import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
class Spatial_Position(models.Model):

  UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=100,  help_text ="e.g. Klimaaggregat_Pos_1", verbose_name= "Spatial Position Name",  editable=True, default= None)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  owner = models.ForeignKey("BoltMan.ProjectUser_BoltMan_Ref", models.SET_NULL, blank=True,null=True,)

  x= models.FloatField(editable=True, verbose_name= "X Coordinate [mm]:", default= 0)
  y= models.FloatField(editable=True, verbose_name= "Y Coordinate [mm]:", default= 0)
  z= models.FloatField(editable=True, verbose_name= "Z Coordinate [mm]:", default= 0)

  xn=models.FloatField(editable=True, verbose_name= "X orientation Vector []:", default= 0, validators=[MaxValueValidator(-1),MinValueValidator(1)])
  yn=models.FloatField(editable=True, verbose_name= "Y orientation Vector []:", default= 0, validators=[MaxValueValidator(-1),MinValueValidator(1)])
  zn=models.FloatField(editable=True, verbose_name= "Z orientation Vector []:", default= 1, validators=[MaxValueValidator(-1),MinValueValidator(1)])
  
  class Meta:
    app_label = 'BoltMan'
  def __str__(self):
    return str(self.name) + 'mm X: ' + str(self.x) + 'mm Y: ' + str(self.y) + 'mm Z: ' + str(self.z)
  
def on_create_default_position():
  settings = Spatial_Position(name= "default")
  settings.save()
  return settings.UUID