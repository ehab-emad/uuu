from django.forms import ModelForm
from django import forms
from EcoMan.models import Analysis, Analysis_Comparison
from EcoMan.models import Utilisation_Process
#Edit Utilistaion instance process
class UtilisationInstanceUpdateForm(forms.ModelForm):
    
    forms.FloatField(label='Process Distance [km]', required=True, min_value=0, )      
    def __init__(self, *args, **kwargs): 
        super(UtilisationInstanceUpdateForm, self).__init__(*args, **kwargs)    
        instance = getattr(self, 'instance', None)

    class Meta:
        model = Utilisation_Process
        fields = ('custom_name', 'quantity', 'notes', 'goods_weight' , 'goods_weight_utilisation')
        widgets = {
          'notes': forms.Textarea(attrs={'rows':4, }),
        }
    field_order = ['custom_name', 'quantity', 'goods_weight' , 'goods_weight_utilisation', 'notes',]   

#Add Utilisation Analysis single column
class UtilisationInstanceCreateForm(forms.ModelForm):
    vehicle= forms.ChoiceField(choices = [], label='Vehicle')    

    def __init__(self, *args, **kwargs): 
        super(UtilisationInstanceCreateForm, self).__init__(*args, **kwargs)     
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['id'].widget.attrs['readonly'] = True       

    class Meta:
        model = Analysis
        fields = ('id', ) 

#Add Utilisation Analysis Two Column
class UtilisationInstanceCreateForm_Analysis_Comparison(forms.ModelForm):
    vehicle= forms.ChoiceField(choices = [], label='Vehicle')    

    def __init__(self, *args, **kwargs): 
        super(UtilisationInstanceCreateForm_Analysis_Comparison, self).__init__(*args, **kwargs)     
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['id'].widget.attrs['readonly'] = True       

    class Meta:
        model = Analysis_Comparison
        fields = ('id', ) 
