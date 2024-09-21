from django import forms
from EcoMan.models import *
import json
class ObjectFormParameters(forms.Form):
    '''Workflow_Object Form
    '''
    field_order = []
    def __init__(self, *args, **kwargs):
        json_data = kwargs.pop('instance_parameters', {})
        super(ObjectFormParameters, self).__init__(*args, **kwargs)
        if json_data:
            for key, value in json_data.items():
                # Check if args are provided and if the key exists in args[0]
                if len(args) > 0 and key in args[0]:
                    value = args[0][key]  # Use the value from args[0] if it exists
                # Determine the type of field to create based on the type of value
                if isinstance(value, bool):
                    self.fields[key] = forms.BooleanField(initial=value)
                elif isinstance(value, (int, float)):
                    self.fields[key] = forms.FloatField(initial=value)
                elif isinstance(value, str):
                    self.fields[key] = forms.CharField(initial=value)


    def clean(self):
        cleaned_data = super().clean()
        errors = []
        for field_name, field_value in cleaned_data.items():
            if self.fields[field_name].widget.attrs.get('readonly'):
                continue  # Skip validation for readonly fields
            try:
                # Attempt to convert the value to a float
                float_value = float(field_value)
            except (ValueError, TypeError):
                errors.append((field_name, f'{field_name} must be a valid float.'))
        # Add errors after the iteration
        for field_name, error_message in errors:
            self.add_error(field_name, error_message)
        return cleaned_data
    
