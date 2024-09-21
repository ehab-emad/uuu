from django import forms
from EcoMan.models import *
from CatiaFramework.models import Workflow
import os

class WorkflowForm(forms.ModelForm):
    '''Workflow Form
    '''

    def __init__(self, *args, **kwargs):
        super(WorkflowForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

    class Meta:
        model = Workflow
        fields = '__all__'
        exclude = ['reference_workflow', 'parent_object', 'instruction', 'owner', 'type', 'status', 'project_model', 'is_active', 'accessibility' ]
