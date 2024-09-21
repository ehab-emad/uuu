from django.db import models
from datetime import datetime
from django.urls import reverse
from django.forms.models import model_to_dict
from website.generate_pk import generate_pk
from django.conf import settings
from EcoMan.models.lca_property import Lca_Property
class Lca_Support_Ticket(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)    
    name = models.CharField(max_length=100,  default= 'No Name', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("EcoMan.ProjectUser_EcoMan_Ref", models.SET_NULL, blank=True,null=True,)
    project_model=models.ForeignKey("EcoMan.Project_EcoMan_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a a project for TICKET", default=None, blank=True,null=True, )
    target_object_id = models.CharField(max_length=255,  default= '0', editable=True, blank=True)

    OBJECT_TYPE= [
    ("General", ("General")),       
    ("Analysis", ("Analysis")),
    ("Analysis_Comparison", ("Analysis Comparison")),
    ("Lca_Database", ("LCA Database")), 
    ("Lca_Database_Process", ("LCA Process (Database)")),     
    ("Instance_Idemat_Database_Process", ("LCA Process (Instance)")),     
    ]

    object_type = models.CharField(choices=OBJECT_TYPE, verbose_name="Issued Object", max_length=32, default="ROWS",)

    ISSUE_TYPE= [
    ("FEATURE", ("Feature (Improvement Proposal")),       
    ("BUG", ("Bug (result is wrong or something is not working as expected)")),
    ("DATABASE", ("Database (my job appears to be corrupted)")),
    ("LCA_DATABASE", ("LCA Database (request for new databases and processes)")), 
    ("ARBITRARY", ("Arbitrary")),        
    ]

    issue_type = models.CharField(choices=ISSUE_TYPE, verbose_name="Issue Type", max_length=32, default="ROWS",)
    target_url = models.CharField( verbose_name="Issued URL", max_length=500, default="ROWS",)
    notes = models.TextField(max_length=2000, blank=True, null=True, verbose_name= "Issue Description", help_text="Issue Description") 
    email = models.EmailField(max_length = 254)
    class Meta:
        app_label = 'EcoMan'
    def __str__(self):
        return str(self.name) 