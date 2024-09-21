from django import forms
from EcoMan.models import *
from django.db.models import Q
from CatiaFramework.models import Workflow_Action, Workflow_Object
import os

class ActionForm(forms.ModelForm):
    '''Workflow_Action Form
    '''

    field_order = []
    def __init__(self, *args, **kwargs):
        parent_workflow = kwargs.pop('parent_workflow', None)
        parent_stage = kwargs.pop('parent_stage', None)
        actions =[]
        objects=[]
        target_objects=[]
        for stage in parent_workflow.static_structure:
            for obj in stage['objects']:
              objects.append(obj)
            if stage['UUID'] == str(parent_stage.UUID):
              target_objects = stage['objects']
        #collect all actions in stage
        for obj in objects:      
          for act in obj['actions']:
              actions.append(act)
        for act in stage['actions']:
          actions.append(act)
        sel_actions =[]
        sel_objects=[]
        sel_target_objects=[]
        for obj in objects:
           sel_objects.append((obj['UUID'], obj['name']))
        for obj in target_objects:
           sel_target_objects.append((obj['UUID'], obj['name']))
        for act in actions:
           sel_actions.append((act['UUID'], act['name']))

        super(ActionForm, self).__init__(*args, **kwargs)
        if parent_workflow:   
            self.fields['required_objects'].choices = sel_objects
            self.fields['required_actions'].choices = sel_actions
        if parent_stage:    
            self.fields['target_object'].choices = sel_target_objects
            #self.base_fields['target_object'].choices =[(choice.UUID, choice) for choice in Workflow_Object.objects.filter(parent_stage = str(parent_stage.UUID))]

    class Meta:
        model = Workflow_Action
        exclude = ['parent_stage', 'parent_action', 'parent_object', 'instruction', 'owner', 'status', 'project_model', 'is_public', 'is_active','type','accessibility', ]
        fields = '__all__'


class ActionStageForm(forms.ModelForm):
    '''Workflow_Action Form
    '''

    field_order = []
    def __init__(self, *args, **kwargs):
        parent_workflow = kwargs.pop('parent_workflow', None)
        parent_stage = kwargs.pop('parent_stage', None)
        actions =[]
        objects=[]
        target_objects=[]
        for stage in parent_workflow.static_structure:
            for obj in stage['objects']:
              objects.append(obj)
            if stage['UUID'] == str(parent_stage.UUID):
              target_objects = stage['objects']
        #collect all actions in stage
        for obj in objects:      
          for act in obj['actions']:
              actions.append(act)
        for act in stage['actions']:
          actions.append(act)
        sel_objects=[]
        sel_target_objects=[]
        for obj in objects:
           sel_objects.append((obj['UUID'], obj['name']))
        for obj in target_objects:
           sel_target_objects.append((obj['UUID'], obj['name']))
        super(ActionStageForm, self).__init__(*args, **kwargs)
        if parent_stage:    
            self.fields['target_object'].choices = sel_target_objects
            #self.fields['target_object'].queryset = Workflow_Object.objects.filter(parent_stage = str(parent_stage.UUID))
    class Meta:
        model = Workflow_Action
        exclude = ['is_automatic',
                   'required_actions',
                    'required_objects',
                    'parent_stage',
                    'parent_action',
                      'parent_object',
                        'instruction',
                          'owner',
                            'status',
                              'project_model',
                                'is_public',
                                  'is_active',
                                  'type',
                                  'accessibility', ]
        fields = '__all__'
