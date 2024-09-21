from django import forms
from EcoMan.models import *
from CatiaFramework.models import Workflow_Stage
import os

class StageForm(forms.ModelForm):
    '''Workflow_Stage Form
    '''

    field_order = []
    def __init__(self, *args, **kwargs):
        super(StageForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

    class Meta:
        model = Workflow_Stage
        fields = '__all__'
        exclude = ['parent_stage', 'parent_workflow', 'parent_object', 'instruction', 'owner', 'type', 'status', 'project_model', 'is_active', 'instances']
