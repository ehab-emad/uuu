from django import forms
from NormMan.models import NormParts_Shared_Component
from django.forms.models import model_to_dict
#from django_clamd.validators import validate_file_infection
from NormMan.models import Component_Group_Level
import uuid
class NewSharedComponentForm(forms.ModelForm):

    target_category_uuid = forms.UUIDField()
    def __init__(self, *args, **kwargs):                
        if "request" in kwargs: self.request = kwargs.pop("request")         
        self.target_uuid = kwargs.pop("parent") if "parent" in kwargs else "fd9cea85-83d8-4a79-a1f1-22d1dd578516"
        self.part_uuid = kwargs.pop("uuid") if "uuid" in kwargs else None
        super(NewSharedComponentForm, self).__init__(*args, **kwargs)
        self.new = True if self.part_uuid is None else False
        self.prefilled = True if "files" in kwargs else False
                
        if hasattr(self, 'request'):
            self.initial['owner'] = self.request.user

        self.fields['thumbnail'].validators = [validate_file_infection]
        
        self.fields['owner'].disabled = True    
        self.fields['target_category_uuid'].initial = Component_Group_Level.objects.filter(UUID = self.target_uuid ).get().UUID
        self.fields['target_category_uuid'].widget= self.fields['target_category_uuid'].hidden_widget()
        self.fields['UUID'].initial = uuid.uuid4() if self.new else self.part_uuid
        self.fields['UUID'].widget.attrs['readonly'] = True
        self.pre_fill_fields() if not self.new and not self.prefilled else None
    
    def pre_fill_fields(self):
        norm_part = NormParts_Shared_Component.objects.filter(UUID=self.part_uuid).get()
        if norm_part:
            for field in self.fields.keys():
                try:
                    self.fields[field].initial = getattr(norm_part, field)
                except AttributeError:
                    pass
                pass

        pass

    
    

    class Meta:
        model = NormParts_Shared_Component
        fields = '__all__'
