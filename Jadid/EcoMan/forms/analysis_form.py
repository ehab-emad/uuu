from django import forms
from EcoMan.models import Analysis, Analysis_Settings
from django.forms.models import model_to_dict
from django.core.validators import MinValueValidator, MaxValueValidator
class AnalysisCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AnalysisCreateForm, self).__init__(*args, **kwargs)
        self.fields['is_public'] = forms.BooleanField(initial=False, required=False, label='Publish')        


        self.fields['is_automotive'] = forms.BooleanField(initial=Analysis_Settings._meta.get_field('is_automotive').get_default(), required=False, label='Include Automotive Functionality')

        self.fields['weight_units'] = forms.ChoiceField(
            choices=Analysis_Settings.WEIGHT_UNIT_CHOICES,
            initial=Analysis_Settings.weight_units,
            required=False,
            label=Analysis_Settings.weight_units.field.verbose_name
        )
        self.fields['weight_decimal_points'] = forms.IntegerField(
        initial=Analysis_Settings._meta.get_field('weight_decimal_points').get_default(),
            required=True,
            label=Analysis_Settings.weight_decimal_points.field.verbose_name,
            validators=[
                MinValueValidator(1),
                MaxValueValidator(5)
            ],
                 )
    class Meta:
        model = Analysis
        fields = (  'name',
                    'logo',                  
                    'project_model',
                    'primary_property',
                    'secondary_properties',
                    'goal_definition',
                    'scope_definition',
                    )

        widgets = {
                    'goal_definition': forms.Textarea(attrs={'rows':8, }),
                    'scope_definition': forms.Textarea(attrs={'rows':8, }),
                    }

class AnalysisEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AnalysisEditForm, self).__init__(*args, **kwargs)
        analysis = Analysis.objects.filter(id = self.instance.id).get()
        self.fields['is_public'] = forms.BooleanField(initial=False, required=False, label='Is Analysis Public')
        settings_list  = analysis.analysis_settings.as_list()

        for setting in settings_list:
            if isinstance(setting.value, bool) and "report_" not in setting.name:
                self.fields[setting.name] = forms.BooleanField(initial=setting.value, required=False, label=setting.verbose)

        self.fields['weight_units'] = forms.ChoiceField(
                choices=analysis.analysis_settings.WEIGHT_UNIT_CHOICES,
                initial=analysis.analysis_settings.weight_units,
                required=False,
                label=Analysis_Settings.weight_units.field.verbose_name
            )
        self.fields['weight_decimal_points'] = forms.IntegerField(
                initial=analysis.analysis_settings.weight_decimal_points,
                required=True,
                label=Analysis_Settings.weight_decimal_points.field.verbose_name,
                validators=[
                    MinValueValidator(0),
                    MaxValueValidator(6)
                ],
                 )
                
    class Meta:
        model = Analysis
        fields = (  'name',
                    'logo',                  
                    'project_model',
                    'primary_property',
                    'goal_definition',
                    'scope_definition',
                    )

        widgets = {
                    'goal_definition': forms.Textarea(attrs={'rows':8, }),
                    'scope_definition': forms.Textarea(attrs={'rows':8, }),
                    }



class AnalysisReportEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AnalysisReportEditForm, self).__init__(*args, **kwargs)
        analysis_comparison = Analysis.objects.filter(id = self.instance.id).get()
        settings_list  = analysis_comparison.analysis_settings.as_list()

        for setting in settings_list:
            if isinstance(setting.value, bool) and "report_" in setting.name:
                self.fields[setting.name] = forms.BooleanField(initial=setting.value, required=False, label=setting.verbose)
    class Meta:
        model = Analysis
        fields = ('name',)

class AnalysisImportFromJSONForm(forms.ModelForm):
    '''Analysis Comparison Import from JSON
    '''
    JSON_file = forms.FileField(label= "JSON Import FIle",  required=True,)
    tosandbox = forms.BooleanField(label="Add To Your Sandbox Project (selected project will be ignored) ", required=False, initial=True)
    def __init__(self, *args, **kwargs):
        super(AnalysisImportFromJSONForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Analysis
        fields = ['name', 'project_model']
