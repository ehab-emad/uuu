from django.forms import ModelForm
from django import forms



from BoltMan.models import Friction_Joint

class SingleassessmentFrictionJointForm(forms.ModelForm):
    class Meta:
        model = Friction_Joint
        fields = ['mat_1_name', 'mat_2_name', 'lubrication','friction_av', 'friction_min','friction_max', 'source', 'notes']

