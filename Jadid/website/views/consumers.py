# chat/consumers.py
import json, uuid
import base64
import io
from django.core.files.base import ContentFile
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from website.settings import MEDIA_ROOT
from ..scripts import check_user_room
from ..models import ProjectUser
from CatiaFramework.models import Workflow_Object, Workflow_Session, Workflow_Action
from django.shortcuts import get_object_or_404
class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None

    def connect(self):
        userobj = User.objects.filter(username = self.scope['url_route']['kwargs']['room_name'] ).get()
        room = check_user_room(userobj)
        room_name = room.name
        req_room_name = self.scope['url_route']['kwargs']['room_name']
        if room_name == req_room_name:
            self.room_name = room_name
            self.room_group_name = f'chat_{room_name}'
            self.room = room_name
            self.accept()
            async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )



    def receive(self, text_data=None, bytes_data=None):
        """
        Function that receives message and based on category of
        command, additional activities will be executed. This
        message is returned either internally, from JS or externally
        from VB.net.
          * if an error in code occurs when communication is requested, 
            it automatically closes connection on channels and that 
            leads to direct reconnection in VB.Net 
        """

        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        django_response = None
        if "command" in message:
            match message["command"]:
            
                case "framework_status_update":
                    # -> command from framewrok including a current status of VB.net application

                    projectuser= ProjectUser.objects.filter(user__username = message['user']).get()
                    projectuser.framework_connected= message['framework_status']
                    projectuser.catia_connected = message['catia_status']   

                    # here goes update of versioning
                    # so we have to wait for version of framework                     
                    static_path = "norm_parts/static_files/framework"
                    path = f'{MEDIA_ROOT}/{static_path}/meta.json'.replace("\\","/")
                    with open(path, "r") as meta:
                        meta_data = json.loads(meta.read())
                    current_version = message['version']
                    server_version = None if not meta_data else meta_data["version"]                    
                    projectuser.framework_update = False if current_version == server_version else True
                    projectuser.save()
                    django_response = {'command': 'framework_status_update_available'}                       


                case "framework_execution_status_update":
                    """
                    command =   {
                                'type': 'framework_execution_status_update',
                                'message': json.dumps({
                                    'user': request.user.username, 
                                    'session_uuid': session_uuid,
                                    'action_uuid': action_uuid,
                                    'object_uuid': object_uuid,
                                    'object_instance_uuid': None if instance is None else str(instance.UUID),
                                    'object_instance_name': instance.name,
                                    'object_template_name': template_object.name,
                                    'object_instance_description':instance.description,
                                    'object_template_description': template_object.description,
                                    'target_object_uuid': str(action.target_object.UUID),
                                    'required_objects_instances': required_objects,
                                    'shared_component_uuid': shared_component_uuid,         
                                    'parameters': None  if instance is None else json.dumps(instance.instance_framework_metadata),
                                    'session_parameters': None if new_dict is None else json.dumps(new_dict),
                                    'new_instance': None,
                                })
                                }
                    """
                    projectuser= ProjectUser.objects.filter(user__username = message['user']).get()
                    from CatiaFramework.models import ProjectUser_CatiaFramework_Ref
                    pu_catiaframework = ProjectUser_CatiaFramework_Ref.objects.filter(UUID = projectuser.UUID).get()
                    #new instance was created in catia add it to object
                    target_object = None
                    if 'new_instance' in message.keys(): 
                        if message['new_instance'] is not None:
                            if 'target_object' in message.keys():     
                                if message['target_object'] is not None:
                                    if len(message['target_object']) > 0:
                                        target_object = get_object_or_404(Workflow_Object, UUID=message['target_object']["UUID"])
                                        workflow_session = get_object_or_404(Workflow_Session, UUID=message['session_uuid'])
                                        parameters = target_object.instance_parameters if message['new_instance_parameters'] is None else message['new_instance_parameters']
                                        new_instance = Workflow_Object.objects.create(UUID =message['new_instance'] , 
                                                                                    name = message['object_instance_name'],
                                                                                    status = "COMPLETED", 
                                                                                    type = "INSTANCE", 
                                                                                    owner = pu_catiaframework, 
                                                                                    is_active = True,
                                                                                    workflow_session = workflow_session,
                                                                                    instance_parameters = parameters, 
                                                                                    )
                                        new_instance.save()
                                        all_instances = target_object.instances.all()
                                        for inst in all_instances:   #deactivate all other instances and make currently created active
                                                inst.is_active = False
                                                inst.save()
                                        target_object.instances.add(new_instance)

                    #update status of the workflow session metadata --> check Execution message --> no necessity to update the status it will be saved in brewser session 
                    if 'exec_status' in message and 'action_uuid' in message and 'session_uuid' in message:
                        action= get_object_or_404(Workflow_Action, UUID=message['action_uuid'])
                        workflow_session = get_object_or_404(Workflow_Session, UUID=message['session_uuid'])
                        workflow_session.session_metadata.update({"action_status_" + str(action.UUID): message['exec_status']})
                        workflow_session.save()

                    #inform frontend about new session status
                    django_response = {'command': 'workflow_session_status_update_available',                                      
                                        "user": message["user"],
                                        "trigger_id": "framework_execution_status_update",
                                        "method_id": message["action_uuid"],
                                        "exec_status": None if "exec_status" not in message else message["exec_status"],
                                        "exec_message": None if "exec_message" not in message else message["exec_message"],
                                        "workflow_id": message['workflow_uuid'] if target_object is None else None if target_object.parent_stage is None else str(target_object.parent_stage.parent_workflow.UUID),
                                        "session_id": message['session_uuid'],
                                        "stage_id":  message['stage_uuid'] if target_object is None else None if target_object.parent_stage is None else str(target_object.parent_stage.UUID),
                                        "source": "dotnet"   #trick
                                       } 
                case _: 
                    pass        



        # send chat message event to the room
        if django_response:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {'type': 'framework_command', 'message': json.dumps(django_response)})


    def chat_message(self, event):
        """
        Function sending message to chat room based on give type.
        The type is included in a name of function. 
          * Here would be beneficial to think about concept of 
            message types both for framework and django in future 
        """
        self.send(text_data=json.dumps(event))


    def framework_command(self, event):
        """
        Function sending message to chat room based on give type.
        The type is included in a name of function.
          * Here would be beneficial to think about concept of 
            message types both for framework and django in future 
        """
        self.send(text_data=json.dumps(event))
