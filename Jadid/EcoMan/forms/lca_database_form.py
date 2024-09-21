from django import forms
from django.core.exceptions import ValidationError

from EcoMan.models import Lca_Database, ProjectUser_EcoMan_Ref
from django.shortcuts import get_object_or_404
from website.security import check_if_user_in_roles
class LcaDBForm(forms.ModelForm):
    current_project = forms.CharField(label='Target Project')
    def __init__(self, *args, **kwargs): 
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super(LcaDBForm, self).__init__(*args, **kwargs) 
        
        if hasattr(self, 'request'):
            self.initial['owner'] = get_object_or_404(ProjectUser_EcoMan_Ref, UUID=self.request.user.projectuser.UUID) 
            self.initial['current_project'] = self.request.user.projectuser.current_project.name + " Owner: " + self.request.user.projectuser.current_project.owner.username
        self.fields['current_project'].widget.attrs['readonly'] = True 
        self.fields['id'].widget.attrs['readonly'] = True 
        self.fields['owner'].disabled = True


        if not check_if_user_in_roles(self.request,['edag_worker']):
            self.fields['last_import_document'].label = self.fields['last_import_document'].label + " (function disabled in demo version; file will be ignored)"
            self.fields['last_import_document'].disabled = True
            self.fields['logo'].label = self.fields['last_import_document'].label + " (function disabled in demo version; file will be ignored)"
            self.fields['logo'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        accessibility = cleaned_data.get("accessibility")
        db_owner = ProjectUser_EcoMan_Ref.objects.filter(nickname = self.request.user.projectuser.current_project.owner.username).first()
        session_roles = self.request.session.get('roles', '').split(',')

        if "/be_paramount/app-ecoman/user-professional" in self.request.session['groups']:
            return cleaned_data

        if "PROJECT" == accessibility and Lca_Database.objects.filter(accessibility = "PROJECT", owner = db_owner).count() > 0:
            self.add_error('accessibility', 'Only one database per project can be created for free account!')
        elif "ORGANISATION" == accessibility and Lca_Database.objects.filter(accessibility = "ORGANISATION", owner = db_owner).count() > 0:
            self.add_error('accessibility', 'Only one database per organisation can be created for free account!')
        elif "OPEN" == accessibility and Lca_Database.objects.filter(accessibility = "OPEN", owner = db_owner).count() > 0:
            self.add_error('accessibility', 'Only one open database can be created for free account!')
        return cleaned_data
    class Meta:
        model = Lca_Database
        fields = '__all__' 
        exclude = ('categories','projects')
        field_order = ['id', 'owner', 'current_project']
        widgets = {
                    'note': forms.Textarea(attrs={'rows':8, }),

                    } 

class LcaDBImportExcelForm(forms.ModelForm):
  
    def __init__(self, *args, **kwargs): 
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super(LcaDBImportExcelForm, self).__init__(*args, **kwargs) 
        
        if hasattr(self, 'request'):
            self.initial['owner'] = self.request.user
        self.fields['id'].disabled = True 
        self.fields['owner'].disabled = True 
        self.fields['name'].disabled = True 
    class Meta:
        model = Lca_Database
        fields = ('id','name','owner','last_import_document', )
        widgets = {
                    'note': forms.Textarea(attrs={'rows':8, }),

                    } 
class LcaDBForm_update(forms.ModelForm):
    current_project = forms.CharField(label='Target Project')
    def __init__(self, *args, **kwargs): 
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super(LcaDBForm_update, self).__init__(*args, **kwargs) 
        
        if hasattr(self, 'request'):
            self.initial['owner'] = get_object_or_404(ProjectUser_EcoMan_Ref, UUID=self.request.user.projectuser.UUID) 
            self.initial['current_project'] = self.request.user.projectuser.current_project.name + " Owner: " + self.request.user.projectuser.current_project.owner.username
        self.fields['current_project'].widget.attrs['readonly'] = True 
        self.fields['id'].widget.attrs['readonly'] = True 
        self.fields['owner'].disabled = True 
    class Meta:
        model = Lca_Database
        fields = '__all__' 
        exclude = ('categories','projects', 'last_import_document')
        field_order = ['id', 'owner', 'current_project']
        widgets = {
                    'note': forms.Textarea(attrs={'rows':8, }),

                    } 