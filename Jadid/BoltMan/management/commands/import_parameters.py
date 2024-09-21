from NormMan.models import Component_Group_Level
import os, uuid
from django  import apps
from django.core.serializers.json import DjangoJSONEncoder
from django.core.management.base import BaseCommand
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.db.models.fields.related import ForeignKey
from NormMan.models import Component_Group_Level, Project_NormMan_Ref, ProjectUser_NormMan_Ref
from NormMan.scripts.validate_uuid import is_valid_uuid
import website.settings as settings
from django.apps import apps
import pandas as pd
class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, check_field):
        if isinstance(check_field, ImageFieldFile) or isinstance(check_field, FieldFile):
            return str(check_field)
        elif isinstance(check_field, ForeignKey):
            return str(check_field)
        else:
            return super().default(check_field)

def database_import(app_name, sheet_name, model_name):
    # Step 1: Construct the path to the Excel file in the static folder
    path_excel_file = os.path.join(settings.BASE_DIR, app_name, 'static', app_name, 'Parameters_Database.xlsx')
    
    # Step 2: Read the Excel file (automatically detect all columns)
    df = pd.read_excel(path_excel_file, sheet_name=sheet_name, header=0, na_filter=True)
    
    # Step 3: Replace NaN values with 0
    df = df.fillna(0)
    
    # Step 4: Get the corresponding Django model using get_model
    Model = apps.get_model(app_name, model_name)
    
    # Step 5: Loop through the DataFrame and create or update objects in the database
    for _, row in df.iterrows():
        obj = Model()
        for key in df.columns:
            if hasattr(obj, key):
                setattr(obj, key, row[key])
        obj.save()

    print( f"{len(df)} records have been successfully imported into the {model_name} model.")
    return None


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        '''
        This script is creating objects based on provided excel list (assumed to be stored in app static)
        '''
        from BoltMan.models import Bolt_Material
        database_import('BoltMan', 'Bolt Material', 'Bolt_Material')
        database_import('BoltMan', 'Part Material', 'Part_Material')   
        database_import('BoltMan', 'Friction Joint', 'Friction_Joint')     
        database_import('BoltMan', 'Friction Thread', 'Friction_Thread') 
        database_import('BoltMan', 'Friction Head', 'Friction_Head')     
        #database_import('BoltMan', 'Metric Thread', 'Metric_Thread')   
        return
    

