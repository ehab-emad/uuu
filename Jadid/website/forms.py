from django import forms
from .models import Project, Vehicle, Token, ProjectUser
from django.db.models import Q
class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
    class Meta:
        model = Project
        fields = ('name', 'logo', 'network_number', 'project_manager',)        

class ProjectUserSelectProjectForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs): 
        super(ProjectUserSelectProjectForm, self).__init__(*args, **kwargs)  
        project_user = ProjectUser.objects.filter(UUID = self.instance.UUID).get()
        self.fields['current_project'].queryset = project_user.authorised_projects.filter(~Q(name = "Organisation_LCA_Project"))
        self.fields['current_project'].required = True
        self.fields['user'].disabled = True
        
    class Meta:
        model = ProjectUser
        fields = ('user', 'current_project',) 

class ProjectSelectAuthForm(forms.ModelForm): 
    '''this form allows project owner ta add users to the whitelisted users
    '''
    search_field = forms.CharField(label='Search', required=False)
    def __init__(self, *args, **kwargs): 
        super(ProjectSelectAuthForm, self).__init__(*args, **kwargs)  

        self.fields['name'].disabled = True 
        self.fields['project_manager'].disabled = True         
        self.fields['network_number'].disabled = True      
        
    class Meta:
        model = Project
        fields = ('name','project_manager','network_number')  


class VehicleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs): 
        super(VehicleForm, self).__init__(*args, **kwargs)                       
        self.fields['logo'].widget.attrs['readonly'] = True 

    class Meta:
        model = Vehicle
        fields = ('name', 'logo', 'vehicle_classification', 'target_weight', 'life_distance_in_km','life_time_in_years')        


class TokenForm(forms.ModelForm): 
    '''this form allows project owner ta add users to the whitelisted users
    '''
    projectuser_choice = forms.ModelChoiceField(queryset=ProjectUser.objects.none(), label='User', help_text='Select user to grant token', required = False)


    def __init__(self, *args, **kwargs):
        self.projectusers = kwargs.pop('projectusers',None)
        super(TokenForm, self).__init__(*args, **kwargs)        
        self.fields['projectuser_choice'].queryset= self.projectusers    
    class Meta:
        model = Token
        fields = [ 'token_type', 'max_usage', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})  # Use 'datetime-local' for both date and time
        }



