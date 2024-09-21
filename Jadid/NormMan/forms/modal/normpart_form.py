from django import forms
from django.forms.models import model_to_dict
from NormMan.models import Component_Group_Level
import uuid
class NormPartCreateForm(forms.Form):

    shared_component_type = forms.ChoiceField(choices=())
    target_category_uuid = forms.UUIDField()
    new_component_uuid = forms.UUIDField()     
    name = forms.CharField()   
    configuration_file = forms.FileField( required = False)    
    catia_part = forms.FileField(  required = False)
    thumbnail = forms.FileField(  required = False)    
    stl_thumbnail = forms.FileField( required = False )
    workflow_json = forms.FileField(  required = False)   

    

    def __init__(self, *args, **kwargs):
        shared_component_type = []
        shared_component_type.append(("NormParts_Database_Component","NormParts_Database_Component"))
        shared_component_type.append(("NormParts_Database_Part","NormParts_Database_Part"))
        shared_component_type.append(("NormParts_Database_Section","NormParts_Database_Section"))
        shared_component_type.append(("NormParts_Database_Workflow","NormParts_Database_Workflow"))
        shared_component_type.append(("NormParts_Database_Template","NormParts_Database_Template"))  


        super(NormPartCreateForm, self).__init__(*args, **kwargs)
        self.fields['shared_component_type'].choices = shared_component_type
        self.fields['new_component_uuid'].initial = uuid.uuid4()
        self.fields['new_component_uuid'].widget.attrs['readonly'] = True
        self.fields['target_category_uuid'].initial = Component_Group_Level.objects.filter(UUID = "fd9cea85-83d8-4a79-a1f1-22d1dd578516" ).get().UUID
        self.fields['target_category_uuid'].widget= self.fields['target_category_uuid'].hidden_widget()