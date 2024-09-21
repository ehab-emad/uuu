
from django import forms
from EcoMan.models import Lca_Support_Ticket
from django.urls import reverse
from django.urls import resolve
class LcaSupportTicketForm(forms.ModelForm):

    def __init__(self, *args, **kwargs): 
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super(LcaSupportTicketForm, self).__init__(*args, **kwargs) 
        
        if hasattr(self, 'request'):
            self.initial['owner'] = self.request.user
            self.initial['project_model'] = self.request.user.projectuser.current_project
            #resolve path in request to define issued object type
            
            match = self.request.META.get('HTTP_REFERER') # resolve(self.request.path)
            print(match)
            if 'analysis' in match:
                self.initial['object_type'] = 'Analysis'
            if  'analysis_comparison' in match:
                self.initial['object_type'] = 'Analysis_Comparison'
            if  'lca_db' in match:
                self.initial['object_type'] = 'Lca_Database'
                         
            listOfNumbers = [int(s) for s in match.split('/') if s.isdigit()] 

            pk= None
            for number in listOfNumbers:
                if number >100000000000 and number < 999999999999:
                    pk = number
            if pk:
                self.initial['target_object_id'] = pk
            self.initial['target_url'] = match
        self.fields['owner'].disabled = True 
        self.fields['project_model'].disabled = True    

    def clean_owner(self):
        instance = self.request.user
        if instance:
            return instance
        else:
            return None
        
    def clean_project_model(self):
        instance = self.request.user.projectuser.current_project
        if instance:
            return instance
        else:
            return None     
               
    class Meta:
        model = Lca_Support_Ticket
        fields = '__all__' 
        widgets = {
          'notes': forms.Textarea(attrs={'rows':4, }),
        }
