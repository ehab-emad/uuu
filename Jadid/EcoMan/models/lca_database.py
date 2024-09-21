from django.db import models
from datetime import date
from website.generate_pk import generate_pk
from django.conf import settings
import pathlib
import pandas as pd
import shutil
from django.contrib.staticfiles.storage import staticfiles_storage
from django.dispatch import receiver
from django.db.models.signals import post_save
class Lca_Database(models.Model): #model name should be renamed to LCA_Database
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)    
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("EcoMan.ProjectUser_EcoMan_Ref", models.SET_NULL, blank=True,null=True,)
    note = models.CharField(max_length=100,  default= 'Put your import comment here...', editable=True, blank=True)
    logo = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Database Image")

    ACCESSIBILITY_CHOICES= [
    ("PROJECT", ("Project Related Release")),
    ("ORGANISATION", ("Official Organisation Related Release")),
    ("OPEN", ("Open Source Release")),
    ]
    is_archive = models.BooleanField(default =False, verbose_name="Archived (not selectable)") 
    accessibility = models.CharField(choices=ACCESSIBILITY_CHOICES, max_length=32, default = "PROJECT")
    projects=models.ManyToManyField("EcoMan.Project_EcoMan_Ref", verbose_name="Projects with access", help_text ="Select one or more projects", default=None, blank=True,)     
    last_import_document = models.FileField(upload_to='documents/', verbose_name="Import processes from an Excel File", blank=True, null=True,)
    categories = models.ManyToManyField("EcoMan.Lca_Database_Category", verbose_name="Categories", default=None, blank=True,)

    class Meta:
        app_label = 'EcoMan'
        
    def __str__(self):
        return str(self.id + " " + self.name + " owner:" + self.owner.nickname) 

    def LCADatabaseFileImport(self, iFile=None):
        '''Import Function for LCA Database. will import 
                Step.1 Read imported file and generate list od dictionarys with processes
                Step.2 Generate process with foreign key of self
        '''
        keys = [ 'unit', 'ec_total', 'ec_of_human_health', 'ec_exo_toxicity', 'ec_resource', 
                     'ec_carbon', 'carbon_footprint', 'ced_total', 'recipe2016_endpoint', 'recipe_human_health', 
                     'recipe_eco_toxicity', 'recipe_resources', 'environmental_footprint', 'source']
        keys.extend(['category_id', 'category_name','group_id', 'group_name', 'subgroup_id', 'subgroup_name','name', 'process_id'])
        if iFile == None:         
            if self.last_import_document:
                path_excel_file = self.last_import_document.path
        else:
            path_excel_file = iFile.last_import_document.path 
    
        df = pd.read_excel (path_excel_file, sheet_name='Import', header=0,  usecols="A:V", na_filter=True, dtype={'idemat_id_group':'string','idemat_id_subgroup':'string'})
        df=df.dropna(subset=[key for key in keys if key != 'source'])
        process_dict=dict()
        process=[]

        #Step.1 Search for processes
        for x in range (df.index.size):
            row_data = df.iloc[x].to_dict()
            process_dict = {y:row_data[y] for y in keys}
            process_dict['group_id'] = int(process_dict['group_id'])
            process_dict['subgroup_id'] = int(process_dict['subgroup_id'])

            if process_dict in process:
                pass
            else:
               process.append(process_dict)
               print('New Item Found! ', process_dict['name'],)

        #Step.2 Generate processes
        self.LCADatabaseGenerateProcesses(process)

       

    def LCADatabaseGenerateProcesses(self, process_list):
        '''Function will generate process predefined in file self.last_import_document and connected with self as foreign key
        '''
        for process in process_list:
            print('Adding Process: ', process['name'],)
            process_dict = process
            from EcoMan.scripts import CreateOrGetCategory
            subgroup=CreateOrGetCategory(process) 
            process_dict['subgroup_model'] = subgroup
            process_dict['group_model'] = subgroup.group_model
            process_dict['category_model'] = subgroup.group_model.category_model

            process_dict['database_model'] = self
            process_dict['accessibility'] = "DATABASE_USERS"

            #remove trailing spaces from units - a known issue for Idemat databases

            process_dict['unit'] = process_dict['unit'].strip()


            #remove excel columns which from now one are database objects
            for e in ['category_id', 'category_name', 'group_id', 'group_name', 'subgroup_id', 'subgroup_name']: 
                process_dict.pop(e)

            #create instance of a model
            from EcoMan.models import Lca_Database_Process
            m = Lca_Database_Process(**process_dict)

            m.owner = m.database_model.owner
            m.save()
            print('Added new process:' + m.name)

    def LCADatabaseFileExport(self, username):
        '''Export Function for LCA Database. 
        '''
        #prepare dst folder
        path_excel_file = settings.MEDIA_ROOT + "\\LCA_Database_Exports\\"
        p = pathlib.Path(path_excel_file)
        p.mkdir(parents=True, exist_ok=True)

        name_dst_file = "LCA_DATABASE_EXPORT_" + self.name + "_" + self.id + "_"+ username + "_" + str(date.today()) + ".xlsx"
        dst_path = path_excel_file + name_dst_file


        keys =['process_id','name','category_id','category_name','group_id', 'group_name','subgroup_id','subgroup_name',]

        keys.extend([ 'unit', 'ec_total', 'ec_of_human_health', 'ec_exo_toxicity', 'ec_resource', 
            'ec_carbon', 'carbon_footprint', 'ced_total', 'recipe2016_endpoint', 'recipe_human_health', 
        'recipe_eco_toxicity', 'recipe_resources', 'environmental_footprint', 'source'])

        df = pd.DataFrame()

        #append rows to excel if any processes are reffering the current database
        from EcoMan.models import Lca_Database_Process
        try:
            reffering_processess = Lca_Database_Process.objects.filter(database_model__pk = self.pk)
            if hasattr(reffering_processess, '__iter__'):
                for process in reffering_processess:
                    process_dict = process.__dict__
                    process_dict.pop('id', None)
                    process_dict.pop('created_at', None)
                    process_dict.pop('updated_at', None)
                    process_dict.pop('accessibility', None)
                    process_dict.pop('database_model_id', None)
                    #process_dict.pop('_state', None)

                    #ADD FOREIGNKEY VALUES
                    process_dict['category_id'] =process.category_model.identifier
                    process_dict['category_name'] =process.category_model.name
                    process_dict['group_id'] =process.group_model.identifier
                    process_dict['group_name'] =process.group_model.name
                    process_dict['subgroup_id'] =process.subgroup_model.identifier
                    process_dict['subgroup_name'] =process.subgroup_model.name
                    process_dict.pop('_state', None)
                    ordered_dict = {k: process_dict[k] for k in keys}  #reorder the dictionary to hold the pattern in the import template
                    df = pd.concat([df, pd.DataFrame([ordered_dict])], ignore_index=True)
            else:
                process_dict = reffering_processess.__dict__
                process_dict.pop('id', None)
                process_dict.pop('created_at', None)
                process_dict.pop('updated_at', None)
                process_dict.pop('accessibility', None)
                process_dict.pop('database_model_id', None)
                process_dict.pop('_state', None)

                #ADD FOREIGNKEY VALUES
                process_dict['category_id'] =reffering_processess.category_model.identifier
                process_dict['category_name'] =reffering_processess.category_model.name
                process_dict['group_id'] =reffering_processess.group_model.identifier
                process_dict['group_name'] =reffering_processess.group_model.name
                process_dict['subgroup_id'] =reffering_processess.subgroup_model.identifier
                process_dict['subgroup_name'] =reffering_processess.subgroup_model.name
                ordered_dict = {k: process_dict[k] for k in keys}  #reorder the dictionary to hold the pattern in the import template
                df = pd.concat([df, pd.DataFrame([ordered_dict])], ignore_index=True)

        except Lca_Database_Process.DoesNotExist:
            reffering_processess = None
        df.to_excel(dst_path, sheet_name='Export', startrow = 0, index = False, header = True, engine ='xlsxwriter',)

        return dst_path

from website.models import ProjectUser
@receiver(post_save, sender=ProjectUser)
def changed_projectuser(sender, instance, created, **kwargs):
    if created:
        return
    else:
        '''
        Find objects which are belonging to user and projects for which user is not authorised   
        '''
        #COllect UUIDS of projects for which user is authorised
        projects = instance.authorised_projects.all()
        project_uuids = []
        for project in projects:
            project_uuids.append(project.UUID)

        #Collect objects belonging to user
        query_lca_database = Lca_Database.objects.filter(owner__UUID = instance.UUID)
        
        #Filter objects belonging to 
        from operator import and_
        from django.db.models import Q
        import functools 
        query_lca_database = query_lca_database.filter(functools.reduce(and_, [~Q(projects__UUID=c) for c in project_uuids]))



        for lca_database in query_lca_database:
            print ("LCA_Database: Orphan Object:" + lca_database.name + "UUID:" + str(lca_database.id) + "owner:" + str(lca_database.owner))
            from EcoMan.models import ProjectUser_EcoMan_Ref
            lca_database.owner = None
            print ("LCA_Database: Anonymous Object:" + lca_database.name + "UUID:" + str(lca_database.id)+ "owner:" + str(lca_database.owner)) 
