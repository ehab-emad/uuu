from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from website.generate_pk import generate_pk
class Concept(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)    
    name = models.CharField(max_length=100,  default= 'No Name', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('ConceptMan.ProjectUser_ConceptMan_Ref', models.SET_NULL, blank=True,null=True,)
    project_model=models.ForeignKey("ConceptMan.Project_ConceptMan_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a a project for analysis", default=None, blank=True, null=True, )

    vehicles=models.ManyToManyField("ConceptMan.Vehicle_ConceptMan_Ref", verbose_name="Vehicles", help_text ="Select one or more vehicles", default=None, blank=True,)   
    logo =models.CharField(default='Default Concept Logo', max_length=1000)
    parts=models.ManyToManyField("ConceptMan.Part", verbose_name="Part", help_text ="Select one or more parts", default=None, blank=True, )  
    weight = models.FloatField(editable=False, verbose_name= "Concept Weight [kg]", blank=True,  default = 0)

    class Meta:
        app_label = 'ConceptMan'
    def __str__(self):
        return str(self.name) 

    def save(self, *args, **kwargs):
        self.calculate_concept_weight() 

        super(Concept, self).save(*args, **kwargs)

    def calculate_concept_weight(self):
        """
        This function estimates the weight of the concept 
        """
        self.weight = 0
        parts_in_use = self.parts.all()
        for x in parts_in_use: 
            self.weight += x.weight      

    from ConceptMan.models import Part
    @receiver(post_save, sender=Part)
    def save_part(sender, instance, **kwargs):
        '''this function will be triggered everytime part will be saved
        '''
        #find all concepts using instance part and save them in order to recalculate concept weight
        from ConceptMan.models import Part
        query_part = Part.objects.filter(id = instance.id)
        query = Concept.objects.filter(parts__in = query_part)

        for object in query:
            object.save()
    #from EcoMan.models import Analysis

    #@receiver(post_save, sender=Analysis)
    #def save_analysis(sender, instance, **kwargs):
    #    '''this function will be triggered everytime analysis will be saved
    #    '''
    #    #find all concepts using instance part and save them in order to recalculate concept weight
    #    from ConceptMan.models import Part
    #    analysis = Analysis.objects.filter(concept_model = self.id).get()
    #    lc_parts = analysis.lca_part_models.all()
        

    #    for lca_part in lc_parts:
    #        parts = lc_part.part_model
    #    query = Concept.objects.filter(parts__in = query_part)

    #    for object in query:
    #        object.save()
