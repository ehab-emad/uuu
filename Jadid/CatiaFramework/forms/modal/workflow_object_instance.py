from django import forms
from EcoMan.models import *
from CatiaFramework.models import Workflow_Object


class WorkflowObjectInstanceForm(forms.ModelForm):
    '''Workflow Form
    '''
    # Define the custom dropdown field
    selected_instance_uuid = forms.CharField(label='Reference Instance UUID', required=True,)


    field_order = []
    def __init__(self, *args, **kwargs):
        object_template = kwargs.pop('object_template', None)
        super(WorkflowObjectInstanceForm, self).__init__(*args, **kwargs)
        self.fields['selected_instance_uuid'].widget.attrs['readonly'] = True
  
    class Meta:
        model = Workflow_Object
        fields = ['name', 'description']
    
class WorkflowObjectInstanceUpdateForm(forms.ModelForm):
    '''Workflow Form
    '''
    # Define the custom dropdown field

    field_order = []
    def __init__(self, *args, **kwargs):
        super(WorkflowObjectInstanceUpdateForm, self).__init__(*args, **kwargs)        

    class Meta:
        model = Workflow_Object
        fields = ['name', 'description']

 