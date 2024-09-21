from django import forms
from EcoMan.models import *
from CatiaFramework.models import Workflow_Instruction
import os

class InstructionForm(forms.ModelForm):
    '''Workflow_Action Form
    '''

    field_order = []
    def __init__(self, *args, **kwargs):
        super(InstructionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

    class Meta:
        model = Workflow_Instruction
        fields = '__all__'
        widgets = {
          'description': forms.Textarea(attrs={'rows':8, }),
        }

