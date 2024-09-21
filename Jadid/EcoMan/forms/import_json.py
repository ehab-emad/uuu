from django.forms import ModelForm
from django import forms
from EcoMan.models import Analysis_Comparison, Analysis




class ImportJsonForm(ModelForm):

    def __init__(self, *args, **kwargs):
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super(ImportJsonForm, self).__init__(*args, **kwargs)

        if hasattr(self, 'request'):
            self.initial['owner'] = self.request.user.projectuser
        self.fields['id'].disabled = True
        self.fields['owner'].disabled = True
    class Meta:
        model = Analysis_Comparison
        fields = ('id', 'name', 'owner', 'last_import_document')

class ImportJsonAnalysisForm(ModelForm):
    JSON_file = forms.FileField(label= "JSON Import FIle",  required=True,)
    def __init__(self, *args, **kwargs):
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super(ImportJsonAnalysisForm, self).__init__(*args, **kwargs)

        if hasattr(self, 'request'):
            self.initial['owner'] = self.request.user.projectuser
        self.fields['id'].disabled = True
        self.fields['owner'].disabled = True
    class Meta:
        model = Analysis
        fields = ('id', 'name', 'owner')