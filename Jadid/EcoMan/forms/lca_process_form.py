from django import forms
from EcoMan.models import Lca_Database_Process
from EcoMan.models import Lca_Database_Group
from EcoMan.models import Lca_Database_Subgroup

class EcoProcessCreateForm(forms.ModelForm):
    #dummy field informing user that this process will belo9ng to him
    owner_dummy = forms.CharField(label='Process ID owner')      
    #dummy field informing user that this process will belong to the currect database
    database_model_dummy = forms.CharField(label='Process ID owner') 

    def __init__(self, *args, **kwargs): 
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super(EcoProcessCreateForm, self).__init__(*args, **kwargs)   
        if hasattr(self, 'request'):
            self.initial['owner'] = self.request.user.projectuser.UUID
            self.fields['owner'].widget= forms.HiddenInput()
            self.initial['database_model'] = self.request.idemat_database           
            self.fields['database_model'].widget= forms.HiddenInput()

            self.initial['owner_dummy'] = self.request.user
            self.initial['database_model_dummy'] = self.request.idemat_database 
            self.initial['accessibility'] = 'DATABASE_USERS'

        self.fields['owner_dummy'].widget.attrs['readonly'] = True  
        self.fields['owner_dummy'].required = False

        self.fields['database_model_dummy'].widget.attrs['readonly'] = True  
        self.fields['database_model_dummy'].required = False

        self.fields['group_model'].disabled = True 
        self.fields['subgroup_model'].disabled = True 

        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            if 'subgroup_model' in self.data:   #prefil the choice fields on post to overcome error "selected item not valid option"
                subgroup_model_id = self.data['subgroup_model']
                group_model_id = self.data['group_model']
                category_model_id= self.data['category_model']
                self.fields['group_model'].disabled = False
                self.fields['subgroup_model'].disabled = False
                self.fields['group_model'].queryset=Lca_Database_Group.objects.filter(id=group_model_id)
                self.fields['subgroup_model'].queryset=Lca_Database_Subgroup.objects.filter(id=subgroup_model_id)     


    class Meta:
        model = Lca_Database_Process
        fields = '__all__'
        exclude ='id', 'created_at', 'updated_at','engineering_material', 'process_id', 
        widgets = {
                    'source': forms.Textarea(attrs={'rows':4, }),
                    'owner_field': forms.widgets.Textarea(attrs={'is_hidden': False,
                                                                    'disabled': True}),
                    'database_model_field': forms.widgets.Textarea(attrs={'required': False,
                                                                    'disabled': True}),          
        }

class EcoProcessEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs): 
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super(EcoProcessEditForm, self).__init__(*args, **kwargs)   
        if hasattr(self, 'request'):
            self.initial['owner'] = self.request.user.projectuser.UUID     
        model_fields = [field.name for field in Lca_Database_Process._meta.get_fields()]
        model_fields.remove('id')
        model_fields.remove('created_at')
        model_fields.remove('updated_at')
        
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:

                self.fields['process_id'].widget.attrs['readonly'] = True              
                self.fields['unit'].widget.attrs['readonly'] = True  
                self.fields['database_model'].widget.attrs['readonly'] = True
                self.fields['owner'].widget.attrs['readonly'] = True
                self.fields['process_id'].disabled = True 
                self.fields['unit'].disabled = True
                self.fields['database_model'].widget.attrs['readonly'] = True         
                self.fields['owner'].widget.attrs['readonly'] = True

    class Meta:
        model = Lca_Database_Process
        fields = '__all__'
        exclude ='id', 'created_at', 'updated_at','engineering_material'
        widgets = {
          'notes': forms.Textarea(attrs={'rows':4, }),
        }
#LCA Process Review form
class LcaProcessReviewForm(forms.ModelForm):
    owner_process_dummy = forms.CharField(label='Process ID owner')  
    database_name_dummy = forms.CharField(label='Database Name')  
    accessibility_dummy = forms.CharField(label='Accessibility')     
    unit_dummy = forms.CharField(label='Unit')      
    process_owner_dummy = forms.CharField(label='Process Owner')


    category_name_dummy = forms.CharField(label='Category Name')        
    group_name_dummy = forms.CharField(label='Group Name')
    subgroup_name_dummy = forms.CharField(label='Group Name')

    def __init__(self, *args, **kwargs): 
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super(LcaProcessReviewForm, self).__init__(*args, **kwargs)   
        if hasattr(self, 'request'):
            process = Lca_Database_Process.objects.filter(id = self.instance.id).get()
            self.initial['process_owner_dummy'] = process.owner.nickname   if not process.owner is None else "Anonymous" 
            self.initial['category_name_dummy'] = process.category_model.identifier + ": " + process.category_model.name
            self.initial['group_name_dummy'] = process.group_model.identifier + ": " + process.group_model.name
            self.initial['subgroup_name_dummy'] = process.subgroup_model.identifier + ": " + process.subgroup_model.name            
            self.initial['database_name_dummy'] = process.database_model.id + ": " + process.database_model.name
            self.initial['accessibility_dummy'] = process.accessibility
        model_fields = [field.name for field in Lca_Database_Process._meta.get_fields()]
        model_fields.remove('id')
        model_fields.remove('created_at')
        model_fields.remove('updated_at')
        
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:

                #left section
                self.fields['name'].widget.attrs['readonly'] = True
                self.fields['process_id'].widget.attrs['readonly'] = True              
                self.fields['process_owner_dummy'].widget.attrs['readonly'] = True 
                self.fields['database_name_dummy'].widget.attrs['readonly'] = True 
                self.fields['accessibility_dummy'].widget.attrs['readonly'] = True 

                self.fields['unit'].disabled = True
        
                #middle section
                self.fields['unit'].widget.attrs['readonly'] = True  
                self.fields['source'].widget.attrs['readonly'] = True 

                #right section
                self.fields['category_name_dummy'].widget.attrs['readonly'] = True  
                self.fields['group_name_dummy'].widget.attrs['readonly'] = True 
                self.fields['subgroup_name_dummy'].widget.attrs['readonly'] = True 

                #Basis
                self.fields['carbon_footprint'].widget.attrs['readonly'] = True  
                self.fields['ced_total'].widget.attrs['readonly'] = True 
                self.fields['environmental_footprint'].widget.attrs['readonly'] = True 

                #Costs
                self.fields['ec_total'].widget.attrs['readonly'] = True  
                self.fields['ec_of_human_health'].widget.attrs['readonly'] = True
                self.fields['ec_exo_toxicity'].widget.attrs['readonly'] = True
                self.fields['ec_resource'].widget.attrs['readonly'] = True
                self.fields['ec_carbon'].widget.attrs['readonly'] = True

                #Recipe
                self.fields['recipe2016_endpoint'].widget.attrs['readonly'] = True  
                self.fields['recipe_human_health'].widget.attrs['readonly'] = True
                self.fields['recipe_eco_toxicity'].widget.attrs['readonly'] = True
                self.fields['recipe_resources'].widget.attrs['readonly'] = True
                self.fields['ec_carbon'].widget.attrs['readonly'] = True
 
    class Meta:
        model = Lca_Database_Process
        fields = '__all__'
        exclude ='id', 'created_at', 'updated_at','engineering_material'
        widgets = {
          'source': forms.Textarea(attrs={'rows':3, }),
        }



