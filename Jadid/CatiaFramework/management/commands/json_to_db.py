import os, json, uuid
from django.core.management.base import BaseCommand
from CatiaFramework.models import *    
from NormMan.models import *                     


del_keys = ['CLASS_name', 'instances', 'actions', 'objects', 'required_actions', 'required_objects']


def recursively_create(in_dict: dict, UUID_parent: uuid.UUID = None) -> None:
    """
    Modification of non complementary fields of dictionary
    obtained from transition from class to dictionary.
    """
    if UUID_parent and 'CLASS_name' in in_dict:
        # -> create object
        # here we would need to have some logic to adapt ids perhaps
        match in_dict["CLASS_name"]:
            case "Workflow":
                model = Workflow
            case "Workflow_Stage":
                model = Workflow_Stage
            case "Workflow_Object":
                model = Workflow_Object
            case "Workflow_Action":
                model = Workflow_Action
        new_object = model.objects.create(pk=in_dict)
        pass
    for key, value in in_dict.items():
        match key:
            case "workflow":
                # here would go unpacking, however idk how to handle it recursively

                pass
            case "structure":
                # here would go unpacking, however idk how to handle it recursively
                pass
            case _:
                # some default case, perhaps for recursion?
                pass


        if isinstance(value, ImageFieldFile):
            if value:
                path = str(os.path.relpath(value.path))
                log_med = [int(obj == 'media') for obj in path.split(os.sep)]
                log_med_shifted = log_med[1:] + [log_med[0]]
                media_extra = [1 if log + log_shifted > 1 else 0 for log, log_shifted in zip(log_med, log_med_shifted)]
                path = os.path.join(*[spl for spl, log in zip(path.split(os.sep), media_extra) if not log])
                in_dict[key] = path
            else:
                in_dict[key] = None
        if isinstance(value, dict):
            recursively_create(value)
        if isinstance(value, list):
            [recursively_create(obj) for obj in value if isinstance(obj, dict)]  


def reset_all():
    for obj in Workflow_Action.objects.all():
        try:
            obj.delete() 
        except:
            pass

    for obj in Workflow_Object.objects.all():
        try:
            obj.delete() 
        except:
            pass        
    for obj in Workflow_Stage.objects.all():
        try:
            obj.delete() 
        except:
            pass
    for obj in Workflow.objects.all():
        try:
            obj.delete() 
        except:
            pass  

def reset_all_components():
    for obj in NormParts_Shared_Component.objects.all():
        try:
            obj.delete() 
        except:
            pass

    for obj in Component_Group_Level.objects.all():
        try:
            obj.delete() 
        except:
            pass        

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Creation of JSON dictionary then to be used for recreation procedure.
        """
        with open(os.path.join(os.getcwd(), "workflow_dict.json"), "r") as file:
            main_dict = json.load(file)
        templates = main_dict['templates']
        instances = main_dict['instances']

        # reset_all()

        for _, obj in templates.items():
            # Create object template function - but this is if only the workflow is to be created
            workflow_dict = obj['workflow']
            input_dict = workflow_dict.copy()
            match input_dict["CLASS_name"]:
                case "Workflow":
                    model = Workflow
                case "Workflow_Stage":
                    model = Workflow_Stage
                case "Workflow_Object":
                    model = Workflow_Object
                case "Workflow_Action":
                    model = Workflow_Action
            
            [input_dict.pop(key) for key in workflow_dict if key in del_keys]            
            # Structurehas extra two params, actions and objects. They have to be ignored as well.
            # we can reduce what is not needed
            # model.objects.filter(pk=input_dict['UUID']).get().delete()                    
            input_dict['project_model'] = Project_CatiaFramework_Ref.objects.get_or_create(pk = input_dict['project_model'])[0]
            input_dict['owner'] =  ProjectUser_CatiaFramework_Ref.objects.get_or_create(pk = input_dict['owner'])[0]
            input_dict['instruction'] = Workflow_Instruction.objects.get_or_create(pk = input_dict['instruction'])[0]      
            new_object = None if model.objects.filter(pk=input_dict['UUID']) else model.objects.create(**input_dict)    

            # -> so now it is needed to pass some references to another object's creation
            # actually, that should not be needed because if we go in a cascade order, 
            # then we always have the objects created beforehand
            structure_dict = obj['structure']
            for struct in structure_dict:
                # ----> region creation of model
                input_dict = struct.copy()
                match input_dict["CLASS_name"]:
                    case "Workflow":
                        model = Workflow
                    case "Workflow_Stage":
                        model = Workflow_Stage
                    case "Workflow_Object":
                        model = Workflow_Object
                    case "Workflow_Action":
                        model = Workflow_Action            
                [input_dict.pop(key) for key in struct if key in del_keys]
                input_dict['project_model'] = Project_CatiaFramework_Ref.objects.get_or_create(pk = input_dict['project_model'])[0]
                input_dict['owner'] =  ProjectUser_CatiaFramework_Ref.objects.get_or_create(pk = input_dict['owner'])[0]
                input_dict['instruction'] = Workflow_Instruction.objects.get_or_create(pk = input_dict['instruction'])[0]
                input_dict['parent_workflow'] = Workflow.objects.filter(pk=input_dict['parent_workflow']).get()
                if 'parent_stage' in input_dict:
                    if input_dict['parent_stage'] is not None:
                        input_dict['parent_stage'] = Workflow_Stage.objects.filter(pk=input_dict['parent_stage']).get()
                new_object = None if model.objects.filter(pk=input_dict['UUID']) else model.objects.create(**input_dict)    
                # ----> endregion creation of model
                if 'actions' in struct:
                    # we want to recursively run
                    for action in struct['actions']:
                        # -> so semewhere hop into a function and then
                        recursively_create_temp(action)
                    pass
                if 'objects' in struct:
                    # we want to recursively run
                    # -> the same as with actions
                    for obj in struct['objects']:
                        # -> so semewhere hop into a function and then
                        recursively_create_temp(obj)
                    pass


        # recursively_create(templates), recursively_create(instances)
        breakpoint()

def recursively_create_temp(in_dict):
    # ----> region creation of model
    input_dict = in_dict.copy()
    match input_dict["CLASS_name"]:
        case "Workflow":
            model = Workflow
        case "Workflow_Stage":
            model = Workflow_Stage
        case "Workflow_Object":
            model = Workflow_Object
        case "Workflow_Action":
            model = Workflow_Action            
    [input_dict.pop(key) for key in in_dict if key in del_keys]
    # -> project_model
    if 'project_model' in input_dict:
        if input_dict['project_model'] is not None:
            input_dict['project_model'] = Project_CatiaFramework_Ref.objects.get_or_create(pk = input_dict['project_model'])[0]
    input_dict['owner'] =  ProjectUser_CatiaFramework_Ref.objects.get_or_create(pk = input_dict['owner'])[0]
    input_dict['instruction'] = Workflow_Instruction.objects.get_or_create(pk = input_dict['instruction'])[0]
    if 'parent_action' in input_dict:
        if input_dict['parent_action'] is not None:
            input_dict['parent_action'] = Workflow_Action.objects.filter(pk=input_dict['parent_action']).get()
    # -> parent_object
    if 'parent_object' in input_dict:
        if input_dict['parent_object'] is not None:
            input_dict['parent_object'] = Workflow_Object.objects.filter(pk=input_dict['parent_object']).get()
    # -> parent_stage
    if 'parent_stage' in input_dict:
        if input_dict['parent_stage'] is not None:
            input_dict['parent_stage'] = Workflow_Stage.objects.filter(pk=input_dict['parent_stage']).get()
    new_object = None if model.objects.filter(pk=input_dict['UUID']) else model.objects.create(**input_dict)      
    # ----> endregion creation of model
    if 'actions' in in_dict:
        # we want to recursively run
        for action in in_dict['actions']:
            # -> so semewhere hop into a function and then
            recursively_create_temp(action)
        pass
    if 'objects' in in_dict:
        # we want to recursively run
        # -> the same as with actions
        for obj in in_dict['objects']:
            # -> so semewhere hop into a function and then
            recursively_create_temp(obj)
        pass