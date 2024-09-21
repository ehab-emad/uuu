import os, json
import pandas as pd
from django import apps, forms
from website.settings import BASE_DIR


class SharedComponentSelectorForm(forms.Form):
    norm_parts_collector = list()
    # worklfow_uuid = forms.CharField()
    # session_uuid = forms.CharField()
    # action_uuid = forms.CharField()
    # request_uuid = forms.CharField()
    # object_uuid = forms.CharField()
    # editor_mode = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.norm_parts_collector.clear()
        group_level = kwargs.get("level", None)
        self.workflow_uuid = kwargs.get('UUID_workflow', None)
        self.action_uuid = kwargs.get('UUID_action', None)  
        self.request_uuid = kwargs.get('UUID_request', None)
        self.object_uuid = kwargs.get('UUID_object', None)   
        self.session_uuid = kwargs.get('UUID_session', None)
        self.editor_mode = kwargs.get('editor_mode', None)   
        to_delete = ['level', 'UUID_workflow', 'UUID_action', 'UUID_request', 'UUID_object', 'UUID_session', 'editor_mode']
        [kwargs.pop(del_attr) for del_attr in to_delete]        
        super(SharedComponentSelectorForm, self).__init__(**kwargs)
        [self.norm_parts_collector.append(SharedComponentConfiguration(meta = obj)) for obj in group_level.normparts_shared_components.all() if obj.project_model_id == args[0]]
        
    class Meta:
        pass

class SharedComponentConfiguration(forms.Form):
    shared_component_type = forms.CharField()
    shared_component_UUID = forms.CharField()
    configuration_select =  forms.ChoiceField()
    meta_data = None

    def __init__(self, *args, **kwargs):
        self.meta_data = kwargs['meta']
        del kwargs['meta']
        args = tuple()
        super(SharedComponentConfiguration, self).__init__(*args, **kwargs)
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