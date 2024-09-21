from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
NONNEGATIVE_VALIDATOR = [MinValueValidator(0),]
class Bolt_Geometry(models.Model):
  UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  owner = models.ForeignKey("BoltMan.ProjectUser_BoltMan_Ref", models.SET_NULL, blank=True,null=True,)

  mthread = models.ForeignKey("BoltMan.Metric_Thread", help_text="Metric Thread", on_delete=models.CASCADE, default=None, related_name='%(class)s_metric_thread', blank=True, null=True) 
  norm = models.CharField(max_length=15,  default= 'Not defined', blank=True, validators=NONNEGATIVE_VALIDATOR,)
  headdiameter = models.FloatField(verbose_name= "Head dieamter:", default = 0, validators=NONNEGATIVE_VALIDATOR, )
  total_length = models.FloatField(verbose_name= "Total length:", default = 0, validators=NONNEGATIVE_VALIDATOR,)
  shank_length = models.FloatField(verbose_name= "Shank length:", default = 0, validators=NONNEGATIVE_VALIDATOR,)
  head_height = models.FloatField(verbose_name= "Head height:", default = 0, validators=NONNEGATIVE_VALIDATOR,)
  thread_size = models.FloatField(verbose_name= "Thread size:", default = 0, validators=NONNEGATIVE_VALIDATOR,)
  thread_metric = models.BooleanField(verbose_name= "Thread is metric:", default = 0)
  thread_right_hand = models.BooleanField(verbose_name= "Thread is right hand:", default = 0)
  picture =  models.CharField(max_length=1000, editable=True)
  tsa  = models.FloatField(editable=True, verbose_name= "Tensile Stress Area (mm^2)", default = 0, validators=NONNEGATIVE_VALIDATOR,)
  material = models.ForeignKey("BoltMan.Bolt_Material", help_text="Select a geometry", on_delete=models.CASCADE, default=None, null=True )
  class Meta:
      app_label = 'BoltMan'
  def __str__(self):
    return 'M' + str(self.thread_size) + ' - Length ' + str(self.thread_size) + 'mm'