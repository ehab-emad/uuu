from CatiaFramework.models import Workflow, Workflow_Object, Workflow_Session
from EcoMan.models import *
from ConceptMan.models import *
from django.shortcuts import redirect
from django.shortcuts import  get_object_or_404
from django.contrib.auth.models import User

def find_dict_in_list(data_list, search_key, search_value):
    """
    Find a dictionary in a list of dictionaries (with potentially nested structures) based on key-value pair.
    
    Args:
    - data_list (list): The list of dictionaries to search in.
    - search_key (str): The key to search for.
    - search_value: The value to match against.
    
    Returns:
    - The dictionary containing the matched key-value pair, or None if not found.
    """
    for item in data_list:
        if isinstance(item, dict):
            if search_key in item and item[search_key] == search_value:
                return item
            # Recursively search nested dictionaries
            elif any(isinstance(v, (dict, list)) for v in item.values()):
                nested_result = find_dict_in_dict(item, search_key, search_value)
                if nested_result is not None:
                    return nested_result
    return None

def find_dict_in_dict(data_dict, search_key, search_value):
    """
    Helper function to find a dictionary in a dictionary based on key-value pair.
    
    Args:
    - data_dict (dict): The dictionary to search in.
    - search_key (str): The key to search for.
    - search_value: The value to match against.
    
    Returns:
    - The dictionary containing the matched key-value pair, or None if not found.
    """
    # Directly check if data_dict contains the key-value pair
    if isinstance(data_dict, dict):
        if search_key in data_dict and data_dict[search_key] == search_value:
            return data_dict
        
        for key, value in data_dict.items():
            # Check if value is a dictionary
            if isinstance(value, dict):
                # Recursively search nested dictionaries
                nested_result = find_dict_in_dict(value, search_key, search_value)
                if nested_result is not None:
                    return nested_result
            # Check if value is a string
            elif isinstance(value, str):
                # Check for key-value pair match
                if key == search_key and value == search_value:
                    return data_dict
            # Check if value is a list of dictionaries
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        nested_result = find_dict_in_dict(item, search_key, search_value)
                        if nested_result is not None:
                            return nested_result
    
    return None


def catia_import(request, **kwargs):
    'this function will generate a json file to import it with EcoMan json parser'


    #collect CatiaFramework Session objects
    session_uuid =kwargs.get('uuid_session', None)
    session = get_object_or_404(Workflow_Session, UUID = str(session_uuid))
    workflow = get_object_or_404(Workflow, UUID = str(session.workflow_model.UUID))
    session_dict = workflow.static_structure

    #collect action custom parameters parameters
    analysis_name = kwargs.get('AnalysisName', 'New QLCA Analysis')
    include_catia_pictures = kwargs.get('IncludeCatiaPartThumbnails', 'False')



    #get corresponding workflow objects templates
    object_template_left_column = find_dict_in_list(session_dict,'name', 'Left Column Parts')['UUID']
    object_template_right_column = find_dict_in_list(session_dict,'name', 'Right Column Parts') ['UUID']
    ab_concept_analysis = find_dict_in_list(session_dict,'name', 'A-B Concept Analysis') ['UUID']


    #get corresponding instances from templates
    query_parts_left_column_instances = get_object_or_404(Workflow_Object, UUID = str(object_template_left_column)).instances.filter(workflow_session__UUID = str(session_uuid)).all()
    query_parts_right_column_instances = get_object_or_404(Workflow_Object, UUID = str(object_template_right_column)).instances.filter(workflow_session__UUID = str(session_uuid)).all()
    ab_concept_analysis_instances = get_object_or_404(Workflow_Object, UUID = str(ab_concept_analysis))

    #create new A-B Concept Analysis Instance (in Framework)
    new_qlca_instance = Workflow_Object.objects.create(workflow_session = session, owner =session.owner, type='INSTANCE', status= 'COMPLETED' )

    ab_concept_analysis_instances.instances.add(new_qlca_instance)
    ab_concept_analysis_instances.save()    
    
    #pass json and redirect
    new_qlca =Analysis_Comparison.objects.create(name = analysis_name)
    UUID_current_project = request.user.projectuser.current_project.UUID
    UUID_current_user = request.user.projectuser.UUID
    new_qlca.owner=get_object_or_404(ProjectUser_EcoMan_Ref, UUID = str(UUID_current_user))
    new_qlca.project_model = get_object_or_404(Project_EcoMan_Ref, UUID = str(UUID_current_project))
    new_qlca.save()

    analysis_left = Analysis.objects.create(project_model = new_qlca.project_model, owner = new_qlca.owner)
    analysis_right = Analysis.objects.create(project_model = new_qlca.project_model, owner = new_qlca.owner)

    concept_model_left=Concept.objects.create(project_model = get_object_or_404(Project_ConceptMan_Ref, UUID = UUID_current_project), 
                                                owner = get_object_or_404(ProjectUser_ConceptMan_Ref, UUID = UUID_current_user))
    concept_model_right=Concept.objects.create(project_model = get_object_or_404(Project_ConceptMan_Ref, UUID = UUID_current_project), 
                                                owner = get_object_or_404(ProjectUser_ConceptMan_Ref, UUID = UUID_current_user))
    analysis_left.concept_model = concept_model_left
    analysis_right.concept_model = concept_model_right
    userobj = User.objects.get(id=request.user.id)
    analysis_left.concept_model.vehicles.add(get_object_or_404(Vehicle_ConceptMan_Ref, UUID = userobj.projectuser.sandbox_vehicle.UUID))
    analysis_right.concept_model.vehicles.add(get_object_or_404(Vehicle_ConceptMan_Ref, UUID = userobj.projectuser.sandbox_vehicle.UUID))


    analysis_left.concept_model.name = "Left Catia Product"
    analysis_left.name = "Left Catia Product"
    analysis_right.concept_model.name = "Right Catia Product"
    analysis_right.name = "Right Catia Product"

    from EcoMan.forms import Analysis_Settings
    analysis_settings = Analysis_Settings.objects.create(name=(new_qlca.name + " settings"))
    analysis_settings.is_public = False

    analysis_settings.save()
    analysis_left.save()
    analysis_right.save()
    concept_model_left.save()
    concept_model_right.save()

    new_qlca.analysis_left = analysis_left
    new_qlca.analysis_right = analysis_right
    new_qlca.analysis_settings = analysis_settings
    new_qlca.playground = True

    #new_qlca.logo = form.cleaned_data.get('logo')
    new_qlca.save()

    #fill parts on the left column
    for part in query_parts_left_column_instances.all():
        if part.instance_parameters:
            density = float(part.instance_parameters['Density'].replace(',','.'))
            volume = float(part.instance_parameters['Volume'].replace(',','.'))
            weight = density * volume
        else:
            weight =0.000000001 #when parameter could not be retrieved correctly
        
        new_part =Lca_Part.objects.create(name = part.name)
        new_part.part_model = Part.objects.create(name = part.name, weight =weight)            
        if part.thumbnail:        
        #     new_part.part_model.logo = part.thumbnail.file
            new_part.part_model.logo.save(
                part.thumbnail.name,
                part.thumbnail.file,
                save=True
            )
            new_part.part_model.save()
        new_part.save()
        analysis_left.lca_part_models.add(new_part)

    #fill parts on the right column
    for part in query_parts_right_column_instances.all():
        if part.instance_parameters:
            density = float(part.instance_parameters['Density'].replace(',','.'))
            volume = float(part.instance_parameters['Volume'].replace(',','.'))
            weight = density * volume
        else:
            weight =0.000000001 #when parameter could not be retrieved correctly
        
        new_part =Lca_Part.objects.create(name = part.name)
        new_part.part_model = Part.objects.create(name = part.name, weight =weight)
        new_part.part_model.logo = part.thumbnail
        new_part.save()
        analysis_right.lca_part_models.add(new_part)

    return redirect('EcoMan:analysis_comparison_detail_view', pk = new_qlca.id)
