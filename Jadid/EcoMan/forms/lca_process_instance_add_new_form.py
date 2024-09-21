from django import forms
from EcoMan.models import Lca_Database_Process
from EcoMan.models import Lca_Part
from EcoMan.models import Lca_Database



#Below not utilised?


#Add Material
class Lca_Part_Add_Material_Form(forms.ModelForm):
    lca_database_choice = forms.ChoiceField(choices = [], label='LCA Database', help_text='Select LCA database source for processs', required = False)  
    lca_group_choice = forms.ChoiceField(choices = [], label='Material Group', help_text='Select Material group')  
    lca_subgroup_choice = forms.ChoiceField(choices = [], label='Material SubGroup', help_text='Select Material subgroup')  
    lca_process_choice= forms.ChoiceField(choices = [], label='Material', help_text='Select Material')    
    quantity = forms.FloatField(required=False, min_value=0, initial=0.0, label='Quantity: Unit according to Idemat. You can leave it as ''0'' and edit it later')
    widget=forms.NumberInput(attrs={'id': 'quantity', 'step': "0.1"})
    #### ToDo: search functions will be implemented in the near future

    def __init__(self, *args, **kwargs): 
        self.weight_unit = kwargs.pop('weight_unit', None)
        self.weight_decimals = kwargs.pop('weight_decimals', None)
        super(Lca_Part_Add_Material_Form, self).__init__(*args, **kwargs)       
        instance = getattr(self, 'instance', None)
        self.fields['id'].widget = forms.HiddenInput()
        self.fields['id'].label = False
        if instance and instance.pk:
            self.fields['id'].widget.attrs['readonly'] = True
            if hasattr(self, 'request'):
                self.initial['owner'] = self.request.user        

            if 'lca_process_choice' in self.data:   #prefil the choice fields on post to overcome error "selected item not valid option"
                database_id = self.data['lca_database_choice']
                group_id = self.data['lca_group_choice']
                subgroup_id = self.data['lca_subgroup_choice']
                process_id= self.data['lca_process_choice']
                o_database=Lca_Database.objects.get(id=database_id)
                o_process=Lca_Database_Process.objects.get(id=process_id)
                self.fields['lca_database_choice'].choices.append((o_database.id, o_database.name))
                self.fields['lca_group_choice'].choices.append((o_process.group_model.id, o_process.group_model.name))
                self.fields['lca_subgroup_choice'].choices.append((o_process.subgroup_model.id, o_process.subgroup_model.name))
                self.fields['lca_process_choice'].choices.append((o_process.id, o_process.name + " Unit:[" + o_process.unit + "]"))

    class Meta:
        model = Lca_Part
        fields = ('id',) 






#Add Process
class Step1UpstreamForm_Process(forms.ModelForm):
    idemat_database_choice = forms.ChoiceField(choices = [], label='Idemat Database', help_text='Select LCA database source for processs')  
    process_group_choice = forms.ChoiceField(choices = [], label='Material Group', help_text='Select process group')  
    process_choice= forms.ChoiceField(choices = [], label='Material', help_text='Select process')    
    quantity = forms.FloatField(required=False, min_value=0, initial=0.0, label='Quantity: Unit according to Idemat. You can leave it as ''0'' and edit it later')
    widget=forms.NumberInput(attrs={'id': 'quantity', 'step': "0.1"})

    def __init__(self, *args, **kwargs): 
        super(Step1UpstreamForm_Process, self).__init__(*args, **kwargs)       
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['id'].widget.attrs['readonly'] = True
            if hasattr(self, 'request'):
                self.initial['owner'] = self.request.user        
            model_fields = [field.name for field in Lca_Database_Process._meta.get_fields()]
            model_fields.remove('id')

            if 'process' in self.data:   #prefil the choice fields on post to overcome error "selected item not valid option"
                database_id = self.data['idemat_database_choice']
                group_id = self.data['process_group_choice']
                process_id= self.data['process_choice']
                o_database=Lca_Database.objects.get(id=database_id)
                o_process=Lca_Database_Process.objects.get(id=process_id)
                self.fields['idemat_database_choice'].choices.append((o_database.id, o_database.name))
                self.fields['process_choice'].choices.append((o_process.id, o_process.name + " Unit:[" + o_process.unit + "]"))
                self.fields['process_group_choice'].choices.append((o_process.group_model.id, o_process.group_model.name))

    class Meta:
        model = Lca_Part
        fields = ('id',) 

#Add Transport
class Step1UpstreamForm_Transport(forms.ModelForm):
    #Idemat_Transport = forms.ChoiceField(choices = [], label='Idemat Transport')
    quantity = forms.FloatField(required=True, min_value=0, initial=0.0, label='Quantity [km]')
    widget=forms.NumberInput(attrs={'id': 'quantity', 'step': "0.1"})
    idemat_database_choice = forms.ChoiceField(choices = [], label='Idemat Database', help_text='Select LCA database source for processs')  
    process_group_choice = forms.ChoiceField(choices = [], label='Material Group', help_text='Select Transport group')  
    process_choice= forms.ChoiceField(choices = [], label='Material', help_text='Select Transport')    
    quantity = forms.FloatField(required=False, min_value=0, initial=0.0, label='Quantity: Unit according to Idemat. You can leave it as ''0'' and edit it later')
    widget=forms.NumberInput(attrs={'id': 'quantity', 'step': "0.1"})
    def __init__(self, *args, **kwargs): 
        super(Step1UpstreamForm_Transport, self).__init__(*args, **kwargs)       
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['id'].widget.attrs['readonly'] = True
            if hasattr(self, 'request'):
                self.initial['owner'] = self.request.user        
            model_fields = [field.name for field in Lca_Database_Process._meta.get_fields()]
            model_fields.remove('id')

            if 'process' in self.data:   #prefil the choice fields on post to overcome error "selected item not valid option"
                database_id = self.data['idemat_database_choice']
                group_id = self.data['process_group_choice']
                process_id= self.data['process_choice']
                o_database=Lca_Database.objects.get(id=database_id)
                o_process=Lca_Database_Process.objects.get(id=process_id)
                self.fields['idemat_database_choice'].choices.append((o_database.id, o_database.name))
                self.fields['process_choice'].choices.append((o_process.id, o_process.name + " Unit:[" + o_process.unit + "]"))
                self.fields['process_group_choice'].choices.append((o_process.group_model.id, o_process.group_model.name))
    class Meta:
        model = Lca_Part
        fields = ('id',) 
        field_order = ['idemat_database_choice', 'process_group_choice', 'process_choice','quantity']  
