from EcoMan.models import Analysis
from django.forms import ModelForm
from django import forms
class Lca_Part_Add_From_Template_Form(forms.ModelForm):
    lca_part_source = forms.ChoiceField(choices=[('1', 'Current Project'), ('2', 'EDAG LCA Part Template Database')]) 
    part_name = forms.CharField(label='Part Name', required=True)
    search_field = forms.CharField(label='Search', required=False)
    selected_template_id = forms.IntegerField(label='Template ID', required=False,)
    selected_template_name = forms.CharField(label='Template Name', required=False,)
    selected_template_notes = forms.CharField(label='Template Notes', required=False, widget=forms.Textarea(attrs={"rows": 6,}))
    def __init__(self, *args, **kwargs): 
        super(Lca_Part_Add_From_Template_Form, self).__init__(*args, **kwargs)  
        self.fields['selected_template_id'].widget.attrs['readonly'] = True
        self.fields['selected_template_name'].widget.attrs['readonly'] = True
        self.fields['selected_template_notes'].widget.attrs['readonly'] = True
        self.fields['id'].widget.attrs['readonly'] = True
    class Meta:
        model = Analysis
        fields = ('id',) 

