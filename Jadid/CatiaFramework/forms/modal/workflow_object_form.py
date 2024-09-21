from django import forms
from EcoMan.models import *
from django.db.models import Q
from CatiaFramework.models import Workflow_Object, Workflow_Action
import os


class ObjectForm(forms.ModelForm):
    '''Workflow_Object Form
    '''
    field_order = []
    def __init__(self, *args, **kwargs):
        parent_workflow = kwargs.pop('parent_workflow', None)
        super(ObjectForm, self).__init__(*args, **kwargs)
        if parent_workflow:  

            instancja = self.instance
            root_instancja = instancja.get_root_object()
            stage = root_instancja.parent_stage            
            all_objects = instancja.get_parent_templates()
            if stage:
                for stage_obj in stage.get_parent_stages():
                    last_obj = stage_obj.get_root_objects().first().get_last_object()
                    all_objects += last_obj.get_all_templates()
            

            self.fields['required_objects'].choices =  [(obj.UUID, obj.name) for obj in all_objects]
            self.fields['required_actions'].queryset = Workflow_Action.objects.filter(Q(parent_stage__parent_workflow__UUID = str(parent_workflow.UUID)) | Q(parent_object__parent_stage__parent_workflow__UUID = str(parent_workflow.UUID)))

        json_data = self.initial.get('instance_parameters', {})
        if json_data:
            for key, value in json_data.items():
                self.fields[key] = forms.CharField(initial=value)   

    def clean(self):
        cleaned_data = super().clean()           
        # Validate your data as needed
        # For example, you can check if required fields are present or if the data is in the correct format.
        return cleaned_data
    
    class Meta:
        model = Workflow_Object
        fields = '__all__'
        exclude = ['parent_stage', 'parent_workflow', 'parent_object', 'instruction', 'owner', 'type', 'status', 
                   'project_model', 'is_active','is_public' , 'is_interactive', 'instances', 'accessibility', 'reference_instance', 'workflow_session']
        parameter_fields = ['object_parameters']