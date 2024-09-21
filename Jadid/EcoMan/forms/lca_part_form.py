from django.forms import ModelForm
from django import forms
from django.forms import ValidationError
from EcoMan.models import *
from ConceptMan.models import *
from website.settings import STATIC_ROOT
import os
class LcaPartForm(forms.ModelForm):
    '''LCA Part
    '''
    part_weight = forms.FloatField(label='Part Weight [kg]', min_value=0)
    part_image = forms.ImageField(label= "Image",  required=False,)
    field_order = ['name', 'part_weight', 'vehicle_weight_participation', 'multiplier', 'part_image' , 'notes', 'istemplate']




    def __init__(self, *args, **kwargs):

        weight_unit = kwargs.pop('weight_unit', None)
        is_automotive = kwargs.pop('is_automotive', None)
        super(LcaPartForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        if instance.part_model:
            if weight_unit == 'KILOGRAMS':
                self.fields['part_weight'].initial = instance.part_model.weight
            else:
                self.fields['part_weight'].initial = instance.part_model.weight  * 1000 
        if weight_unit == 'KILOGRAMS':               
            self.fields['part_weight'].label = 'Part Weight [kg]' 
        else: 
            self.fields['part_weight'].label = 'Part Weight [g]'          
        # Remove vehicle weight participation when not necessary
        if is_automotive == False:
            del self.fields['vehicle_weight_participation']
    class Meta:
        model = Lca_Part
        fields = ['name', 'part_weight', 'vehicle_weight_participation', 'multiplier', 'part_image' , 'notes', 'istemplate']


        widgets = {
                'notes': forms.Textarea(attrs={'rows':4}),
                }
#Add Process
class Lca_Part_Add_Process_Form(forms.ModelForm):
    '''Lca_Part_Add_Process_Form
    '''
    lca_category_choice = forms.ChoiceField(choices = [], label='LCA  category', help_text='Select LCA process category', required = False)
    lca_database_choice = forms.ChoiceField(choices = [], label='LCA Database', help_text='Select LCA database source for processs', required = False)
    lca_group_choice = forms.ChoiceField(choices = [], label='Material Group', help_text='Select Material group')
    lca_subgroup_choice = forms.ChoiceField(choices = [], label='Material SubGroup', help_text='Select Material subgroup')
    lca_process_choice= forms.ChoiceField(choices = [], label='Material', help_text='Select Material')
    quantity = forms.FloatField(required=False, min_value=0, initial=0.0, label='Quantity: Unit according to Idemat. You can leave it as ''0'' and edit it later')
    widget=forms.NumberInput(attrs={'id': 'quantity', 'step': "0.1"})

    def __init__(self, *args, **kwargs):
        super(Lca_Part_Add_Process_Form, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['id'].widget = forms.HiddenInput()
        self.fields['id'].label = False
        if instance and instance.pk:
            self.fields['id'].widget.attrs['readonly'] = True
            if 'lca_process_choice' in self.data.keys():
                database_id = self.data['lca_database_choice']
                category_id = self.data['lca_category_choice']
                group_id = self.data['lca_group_choice']
                subgroup_id = self.data['lca_subgroup_choice']
                process_id= self.data['lca_process_choice']
                o_database=Lca_Database.objects.get(id=database_id)
                o_process=Lca_Database_Process.objects.get(id=process_id)
                self.fields['lca_database_choice'].choices.append((o_database.id, o_database.id))
                self.fields['lca_category_choice'].choices.append((o_process.category_model.id, o_process.category_model.id))
                self.fields['lca_group_choice'].choices.append((o_process.group_model.id, o_process.group_model.id))
                self.fields['lca_subgroup_choice'].choices.append((o_process.subgroup_model.id, o_process.subgroup_model.id))
                self.fields['lca_process_choice'].choices.append((o_process.id, o_process.id))
    class Meta:
        model = Lca_Part
        fields = ('id',)