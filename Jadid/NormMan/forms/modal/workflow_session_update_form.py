from django import forms
from NormMan.models import Workflow_Session
from django.forms.models import model_to_dict

class WorkflowSessionEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(WorkflowSessionEditForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Workflow_Session
        fields = ( 'name' ,)

