from django import forms
from NormMan.models import NormParts_Shared_Component


class SharedComponentFilterForm(forms.ModelForm):
    SEARCH_POLICY = [
    ("AND", "Strict"),
    ("OR", "Liberal"),
    ]

    search_policy = forms.ChoiceField(choices=SEARCH_POLICY,  widget=forms.Select(attrs={'class': 'custom-select'}))
    UUID = forms.UUIDField(required=False, initial=None)

    def __init__(self, *args, **kwargs):                
        if "request" in kwargs: self.request = kwargs.pop("request")         
        super(SharedComponentFilterForm, self).__init__(*args, **kwargs)
        self.fields['UUID'].initial = None
 

    class Meta:
        model = NormParts_Shared_Component
        exclude = ['data_path', 
                   'thumbnail', 
                   'stl_thumbnail',
                   'file_catia_part', 
                   'file_configuration', 
                   'file_workflow_json',
                   'accessibility', 
                   'parameters',
                   'source',
                   'counter']
        # fields = '__all__'
