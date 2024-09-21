import os, uuid
import json as j
from django.db import models
from django.conf import settings
from math import *


class Workflow_Session(models.Model):   #should be LCA_Process
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("NormMan.ProjectUser_NormMan_Ref", models.SET_NULL, blank=True,null=True,)
    is_public = models.BooleanField(default =False, verbose_name="Job will be visible for other colleagues within the same project" )
    workflow_object = models.ForeignKey("NormMan.NormParts_Shared_Component", verbose_name="Parent Category of the Group", on_delete=models.CASCADE,  null=True,)  
    workflow_status = models.JSONField(verbose_name="workflow_status", editable=True, null= True, blank=True)
    created_objects = models.JSONField(default=dict, verbose_name="created_objects", editable=True, null= True, blank=True)        

    class Meta:
        app_label = 'NormMan'        

    def __str__(self):
        return str(f'Object with UUID {str(self.UUID)}')
    
    def update_status(self, json:any = None) -> None:
        """
        Function updates status of a workflow session with respect to given
        input dictionary/string. If string provided, it will be automatically 
        parsed (jsonified) and current workflow status will be then checked 
        in order to find or directly assign inputted value.
        """
        if json:
            try:            
                p = os.path.join(settings.BASE_DIR, self.workflow_object.file_workflow_json.url.strip("/")).replace("\\", "/")
                try:
                    with open(p,"r") as f:
                        meta = j.load(f)
                except:
                    meta = None
                json = json if type(json) is dict else j.loads(json)            
                json.update({"properties_as_string":j.dumps(json["properties"])})
                properties = json["properties"] if "properties" in json else None
                ACTIVE_FLAG = properties["Active"]["value"] if properties is not None and "Active" in properties else None
                ADD_FLAG = True if sum([True if key == json["uid"] else False for key in self.created_objects.keys()]) < 1 else False
                MOD_FLAG = True if not ADD_FLAG and ACTIVE_FLAG else False
                DEL_FLAG = not ACTIVE_FLAG
                if ADD_FLAG or MOD_FLAG:
                    # item does not exist or does exist, should be added or modified here
                    self.created_objects.update({json["uid"]:json})
                    self.created_objects.update({"last_object":json})
                elif DEL_FLAG:
                    # item does exist, should be deleted here
                    del self.created_objects[json["uid"]]
                else:
                    pass
                # -> Modify objects within JSON workflow file
                for key, value in zip(self.workflow_status.keys(), self.workflow_status.values()):
                    if value["id"] == json["parent"]:
                        if "objects" in value:
                            if len(value["objects"]):                            
                                update_at = None
                                for key2, value2 in zip(value["objects"].keys(), value["objects"].values()):
                                    # -> running for objects, where we check if the object exists                                
                                    if value2["uid"] == json["uid"]:
                                        # -> we have found an object, do stuff
                                        update_at = key2
                                if ADD_FLAG and ACTIVE_FLAG:
                                    value["objects"].update({json["uid"]:json})
                                else:
                                    if update_at:
                                        if ACTIVE_FLAG:
                                            value["objects"].update({update_at:json}) 
                                            if "properties" in value["objects"][update_at]:
                                                value["objects"][update_at].update({"properties_as_string":j.dumps(value["objects"][update_at]["properties"])})
                                        else:
                                            del value["objects"][update_at] 
                            else:                                                        
                                value["objects"].update({json["uid"]:json}) if ACTIVE_FLAG else None
                                if len(value["objects"]) != 0:
                                    if "properties" in value["objects"][json["uid"]]:
                                        value["objects"][json["uid"]].update({"properties_as_string":j.dumps(value["objects"][json["uid"]]["properties"])})
                # -> Modify workflow status with meta information
                if meta:
                    for key, value in zip(self.workflow_status.keys(), self.workflow_status.values()):
                        if "m" in key:
                            value.update({"result_object": meta[key]["result_object"]})
                        if "gui" in value:
                            if "icon" in value["gui"]:
                                value["gui"]["icon"] = meta[key]["gui"]["icon"]
                for obj in self.created_objects.values():
                    if "ParentUID" in obj["properties"] and "ParentUID" in json["properties"]:
                        # -> received object is not adapter model, and so the current object is
                        if obj["properties"]["ParentUID"]["value"] == json["properties"]["ParentUID"]["value"]:
                            # -> if they have the same parent
                            if "Type" in obj["properties"] and "Type" in json["properties"]:
                                # -> if they are of same type
                                if obj["properties"]["Type"]["value"] == json["properties"]["Type"]["value"]:
                                    if obj["properties"]["UUID"]["value"] != json["properties"]["UUID"]["value"]:
                                        if "Selected" in obj["properties"]: obj["properties"]["Selected"]["value"] = False #not json["properties"]["Selected"]["value"]
                                        obj.update({"properties_as_string":j.dumps(obj["properties"])})
                    else:
                        if "ParentUID" in json["properties"]:
                            # -> received object is not adapter model
                            pass
                        else:
                            # received object is adapter model and current object is adapter model     
                            if "ParentUID" not in obj["properties"]:
                                if obj["uid"] != json["uid"]:
                                    if "Selected" in obj["properties"]: obj["properties"]["Selected"]["value"] = False #not json["properties"]["Selected"]["value"]
                                    obj.update({"properties_as_string":j.dumps(obj["properties"])})
                        pass   
                for key, value in zip(self.workflow_status.keys(), self.workflow_status.values()):
                    if "w" in key:
                        if "objects" in value:
                            for obj_key in value["objects"].keys():
                                if obj_key != json["uid"]:
                                    value["objects"].update({obj_key:self.created_objects[obj_key]})
                                    pass
                            pass                        
            except Exception as e:
                pass
            self.save()
        else:
            return
        pass



