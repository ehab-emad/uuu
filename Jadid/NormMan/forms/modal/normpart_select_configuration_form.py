from django import forms
from django.forms.models import model_to_dict
from django import forms
from django  import apps
import pandas as pd
import os
from website.settings import BASE_DIR
import json


class NormPartSelectConfigurationForm(forms.Form):
    shared_component_type = forms.CharField()
    shared_component_UUID = forms.CharField()
    configuration_select = forms.ChoiceField()
    norm_parts_collector = None

    def __init__(self, *args, **kwargs):
        instance = kwargs['instance']
        del kwargs['instance']
        super(NormPartSelectConfigurationForm, self).__init__(*args, **kwargs)
        self.fields['shared_component_type'].initial = instance._meta.object_name
        self.fields['shared_component_UUID'].initial = str(instance.UUID)
    @property
    def shared_component_type_property(self):
        return self.fields['shared_component_type'].initial
    
    @property
    def shared_component_UUID_property(self):
        return self.fields['shared_component_UUID'].initial

    class Meta:
        pass


class NormPartSelectConfigurationCollector(forms.Form):
    '''
    So this will be a collector containing form objects
    and it will be a form object as well so as to assure all
    the functionality.
    '''
    norm_parts_collector = list()
    object_id = forms.CharField()
    object_uid = forms.CharField()
    worklfow_uuid = forms.CharField()
    session_uuid = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.norm_parts_collector.clear()
        norm_parts = kwargs.get("norm_parts", None)
        ids = kwargs.get("ids", None)
        del kwargs['norm_parts'], kwargs['ids']
        super(NormPartSelectConfigurationCollector, self).__init__(**kwargs)
        [self.norm_parts_collector.append(Configuration(meta = obj)) for obj in norm_parts if obj.project_model_id == args[0]]
        self.fields['object_id'].initial = ids["id"]
        self.fields['object_uid'].initial = ids["uid"]
        self.fields['worklfow_uuid'].initial = ids["wid"]
        self.fields['session_uuid'].initial = None

    @property
    def object_id_property(self):
        return self.fields['object_id'].initial
    
    @property
    def object_uid_property(self):
        return self.fields['object_uid'].initial

    @property
    def worklfow_uuid_property(self):
        return self.fields['worklfow_uuid'].initial
    
    @property
    def session_uuid_property(self):
        return self.fields['session_uuid'].initial
        
    class Meta:
        pass

class Configuration(forms.Form):
    shared_component_type = forms.CharField()
    shared_component_UUID = forms.CharField()
    configuration_select =  forms.ChoiceField()
    meta_data = None

    def __init__(self, *args, **kwargs):
        self.meta_data = kwargs['meta']
        del kwargs['meta']
        args = tuple()
        super(Configuration, self).__init__(*args, **kwargs)
        self.fields['shared_component_type'].initial = self.meta_data.name if self.meta_data.name is not None else "None"
        self.fields['shared_component_UUID'].initial = self.meta_data.UUID if self.meta_data.UUID is not None else "None"
        self.fields['configuration_select'].widget = forms.Select(attrs = {"id": self.meta_data.UUID })
        self.fields['configuration_select'].choices = self.load_configurations()
        pass
    @property
    def shared_component_type_property(self):
        prop = self.fields['shared_component_type'].initial
        retval = prop if prop is not None else "None"
        return retval
    
    @property
    def shared_component_UUID_property(self):
        prop = self.fields['shared_component_UUID'].initial
        retval = prop if prop is not None else "None"
        return retval

    def load_configurations(self) -> list:
        shared_component_uuid  = self.meta_data.UUID
        shared_model = apps.apps.get_model('NormMan', "NormParts_Shared_Component").objects.filter(UUID = shared_component_uuid ).get()
        configs = list()            
        path_excel_file = shared_model.file_configuration
        if path_excel_file:
            path_to_file = os.path.join(BASE_DIR, path_excel_file.url.strip("/")).replace("\\", "/")                
            df = pd.read_excel(path_to_file, sheet_name=0, header=0, na_filter=True) if os.path.exists(path_to_file) else None
            if df is not None:
                [configs.append((json.dumps(df.iloc[x].to_dict()), json.dumps(df.iloc[x].to_dict()))) for x in df.index]
        return configs


    class Meta:
        pass