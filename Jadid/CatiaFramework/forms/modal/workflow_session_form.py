from django import forms
from EcoMan.models import *
from CatiaFramework.models import Workflow_Session
import os

class WorkflowSessionForm(forms.ModelForm):
    '''Workflow Form
    '''

    def __init__(self, *args, **kwargs):
        super(WorkflowSessionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

    class Meta:
        model = Workflow_Session
        fields = ['name', 'description']
        # exclude = ['reference_workflow', 'parent_object', 'owner', 'type', 'status', 'project_model', 'is_active',  ]
