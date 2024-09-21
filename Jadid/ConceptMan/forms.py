
from django import forms
from website.models import Vehicle
from website.models import Production_Rate
from ConceptMan.models import Part



class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ('name',  'thickness', 'weight', 'engineering_material',  ) 

class ConceptForm(forms.ModelForm):
    class Meta:
        from ConceptMan.models import Concept
        model = Part
        fields ='__all__' 

class PartFormManufacturingProcess(forms.ModelForm):
    class Meta:
        model = Part
        fields = ('process_model', ) 

class ProductionRateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs): 
        super(ProductionRateForm, self).__init__(*args, **kwargs)                       
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['id'].widget.attrs['readonly'] = True        
    class Meta:
        model = Production_Rate
        fields = '__all__'     
        widgets = {
          'notes': forms.Textarea(attrs={'rows':8, }),
        }
        #, 'production_rate_model', 'production_time', 'production_rate_start', 'production_rate_end'