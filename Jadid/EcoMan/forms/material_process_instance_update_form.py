from django.forms import ModelForm
from django import forms
from django.forms import ValidationError
from EcoMan.models import Instance_Idemat_Database_Process

class MaterialProcessInstanceUpdateForm(forms.ModelForm):
    '''
    Edit Process instance idemat process
    '''
    process_name = forms.CharField(label='Used Lca Process Name', required=False)
    process_unit = forms.CharField(label='Lca Process Unit', required=False)
    part_id = forms.IntegerField(label='ID [-]', required=False)
    part_name = forms.CharField(label='Name', required=False)
    part_weight = forms.CharField(label=f'Weight [{"kg"}]', required=False )   
    part_area = forms.FloatField(label='Area [m2]', min_value=0, required=False)

    meq = forms.FloatField(label = 'Material Usage rate [%] a.k.a MEQ', min_value = 100, required=True,)
     
    def __init__(self, *args, **kwargs): 
        self.weight_unit = kwargs.pop('weight_unit', None)
        self.weight_decimals = kwargs.pop('weight_decimals', None)
        super(MaterialProcessInstanceUpdateForm, self).__init__(*args, **kwargs)    
        instance = getattr(self, 'instance', None)


        if instance and instance.pk:
            self.fields['id'].widget.attrs['readonly'] = True  
            self.fields['process_name'].widget.attrs['readonly'] = True 
            self.fields['process_unit'].widget.attrs['readonly'] = True  
            self.fields['part_id'].widget.attrs['readonly'] = True 
            self.fields['part_name'].widget.attrs['readonly'] = True         
            self.fields['part_weight'].widget.attrs['readonly'] = True 
            self.fields['part_weight'].label = f'Weight [kg]'
            self.fields['part_area'].widget.attrs['readonly'] = True 
            self.fields['process_quantity'].label = f'Process Quantity in [kg]'

            #change process quantty according to used units
            #change label if in weight unit set for grams
            if self.weight_unit == "GRAMS":
                self.initial['process_quantity'] = self.initial['process_quantity'] *1000
                self.fields['part_weight'].label= 'Weight [g]'
                self.fields['process_quantity'].label = f'Process Quantity in [g]'

        self.initial['process_quantity'] = f"{self.initial['process_quantity']:.{self.weight_decimals}f}"

    def clean(self):
        cleaned_data = super().clean()

        # Check if 'process_quantity' has to be reversed to kg
        if self.weight_unit =='GRAMS':
            cleaned_data['process_quantity'] = cleaned_data['process_quantity'] /1000

        return cleaned_data

    class Meta:
        model = Instance_Idemat_Database_Process
        fields = ('id','name', 'notes', 'process_quantity', 'is_active',)
        widgets = {
          'notes': forms.Textarea(attrs={'rows':4, }),
        }
    field_order = ['name', 'process_name', 'process_name', 'part_weight', 'part_area',  'meq', 'process_quantity',  'notes', 'id',] 
