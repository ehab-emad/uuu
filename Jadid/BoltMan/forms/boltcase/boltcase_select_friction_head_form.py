from django.forms import ModelForm
from django import forms



from BoltMan.models import Bolt_Case

class BoltcaseSelectFrictionHeadForm(forms.ModelForm):
    class Meta:
        model = Bolt_Case
        fields = ['friction_head']
