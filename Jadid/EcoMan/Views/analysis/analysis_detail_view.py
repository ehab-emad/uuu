import json
from django.shortcuts import  get_object_or_404, redirect
from django.views import generic
from EcoMan.models import Analysis
from EcoMan.models import Instance_Idemat_Database_Process
from django.http import HttpResponseRedirect
from EcoMan.QLCA_Idemat_Calculation import * 
from website.scripts import *
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
import numpy as np
from django.db.models import Count
from django.db.models import Q
from django.contrib import messages
def continue_analysis_detail_view(request):   #this view has to be corrected for analysis objects
    '''User will be redirected to the last edited Analysis Comparison  
    '''

    queryset= Analysis.objects.filter(owner__UUID=str(request.user.projectuser.UUID))
    #filter current_project
    queryset = queryset.filter(project_model = str(request.user.projectuser.current_project.UUID))

    # Filter queryset to exclude objects related to the 'playground'
    queryset = queryset.annotate(parent_left_count=Count('analysis_comparison_Left') ).annotate(parent_right_count=Count('analysis_comparison_Right'))
    # Filter for unused ChildModel instances
    queryset = queryset.filter(Q(parent_left_count=0)  & Q(parent_right_count=0) )

    try:
        obj=queryset.latest('updated_at')
    except:
         messages.info(request, "No recently created object found. Please try in other Project")
         return  redirect('EcoMan:qlca_analysis_welcome_screen')
    url = reverse('EcoMan:analysis_detail_view', kwargs={'pk': obj.id})
    return HttpResponseRedirect(url)

class analysis_detail_view(generic.DetailView):
    model = Analysis
    template_name = 'EcoMan/analysis/analysis_detail_view.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated: #force user to login
            return HttpResponseRedirect('/user/login')
        #check if user has rights to see analysis
        analysis_project_UUID = Analysis.objects.filter(id = kwargs['pk']).get().project_model.UUID
        projects = request.user.projectuser.authorised_projects.all()
        for project in projects:
            if project.UUID == analysis_project_UUID: 
                return super().dispatch(request, *args, **kwargs)
        return HttpResponseRedirect('/eco/index')
        

    def get_object(self):
        
        if 'pk' in self.kwargs:
            peka=int(self.kwargs.get('pk'))
            return get_object_or_404(Analysis, pk=peka) 

        obj= Analysis.objects.filter(owner_id=self.request.user.id)
        obj=obj.filter(playground=True)
        obj=obj.latest('updated_at')

        if not obj:
            return redirect('qlca_welcome_screen')
        else:
            analysis_comparison = get_object_or_404(Analysis, pk=int(obj.pk))  
            return  analysis_comparison

        
    def get_context_data(self, **kwargs):      
        context = super().get_context_data(**kwargs)
        current_analysis_id = self.get_object().pk
        context['current_analysis_id'] = current_analysis_id
        current_analysis =get_object_or_404(Analysis, pk=current_analysis_id)
        #refresh updated_at to mark as last worked on analysis_comparison and to update the values
        current_analysis.save()
        analysis_left = current_analysis          
                  
        analysis_left.save()
        context['analysis_left'] = analysis_left #should be removed in the future
        context['current_analysis'] = analysis_left 
        context['weight_decimals'] = current_analysis.analysis_settings.weight_decimal_points
        context['weight_unit'] = current_analysis.analysis_settings.weight_units
        reference_concept = analysis_left.concept_model
        if reference_concept is not None:
            current_vehicle = reference_concept.vehicles.all()[:1].get().reference_vehicle
        else:
            current_vehicle = self.request.user.projectuser.sandbox_vehicle

        energy_source = current_vehicle.energy_source_model
        context['vehicle'] = current_vehicle
        context['energy_source'] = energy_source
        context['reference_concept'] = reference_concept
        #weights of the concepts        
        context['weight_left_concept']=reference_concept.weight

        lca_parts_left_all = analysis_left.lca_part_models.all().order_by('-id')
        context['lca_parts_left_all'] = lca_parts_left_all
        for part in context['lca_parts_left_all']:
            part.total_weight = part.part_model.weight * part.multiplier
        lca_process_count ={}

        #count the processes for all lca_parts after step
        for entry in lca_parts_left_all:
            lca_process_count ={x: 0 for x, y in Instance_Idemat_Database_Process.LCA_STEP_CHOICES}
            for process in entry.lca_process_model.all():
                lca_process_count[f"{process.lca_step}"] += 1  
            #formulate template expression
            for key, value in lca_process_count.items():
                if value == 0:
                   lca_process_count[key] = "Empty"                
                elif value == 1:
                    lca_process_count[key] = "1 Process"
                else:
                    lca_process_count[key] = f"{value} Processes"   
            entry.lca_process_count = lca_process_count.copy()
            lca_process_count ={}

        context['lca_parts_left_all_list'] = lca_parts_left_all


#weight distribution between parts
        labels_left = []
        data_left = []
        colors_left =[]

        for part in lca_parts_left_all:
            labels_left.append(part.part_model.name)
            data_left.append(part.get_weight_conceptman(current_analysis.analysis_settings.weight_units) * part.multiplier)
            colors_left.append(part.color)

        #doughnut diagram Reference concept
        output_Dict = {
            "labels": [],
            "datasets": [ ]
        }
        colours=[]
        for i in range(len(labels_left)):
            output_Dict["labels"].append(labels_left[i])
            colours.append(colors_left[i] )

        output_Dict["datasets"].append({"data": data_left, "backgroundColor": colours, "borderColor": "#000000",  "borderWidth": 2})
        context['data_parts_doughnut_left_json'] =json.dumps(output_Dict, indent=4)

#SECTION - property Diagrams
        
        property_name = current_analysis.getDefaultProperty().name
        property_verbose_name = current_analysis.getDefaultProperty().verbose_name
        property_unit = current_analysis.getDefaultProperty().unit
        labels_left = []
        data_left = []
        colors_left = []
        entry = {}
        left_total_CO2 = 0
 
        analysis_left_sums= analysis_left.as_dict()
        context['analysis_left_sums'] = analysis_left_sums


        for part in analysis_left_sums['parts'].items():
                labels_left.append(part[1]['name'])
                data_left.append(part[1]['lca_result'][property_name])
                colors_left.append(part[1]['diagram_color'])

        left_total_property = analysis_left_sums['lca_result'][property_name]
        context['left_total_property'] = left_total_property

##CO2 distribution between parts
#    #bar diagram comparison both concepts
        output_Dict = {
            "labels": [" [" + property_unit + "]", " [" + property_unit + "]"],
            "datasets": [ ]
        }
        for i in range(len(labels_left)):
            output_Dict["datasets"].append({"label":labels_left[i],"data":[data_left[i], 0], "stack": 'Left',"backgroundColor": colors_left[i], "borderColor": "#000000",  "borderWidth": 2  })	
        context['data_parts_property_bar_json'] =json.dumps(output_Dict, indent=4)

        #legend table
        legend_dict={}
        for i,j in analysis_left_sums['parts'].items():
            legend_dict[j['name']] = {'value_single': j['lca_part']['lca_result'][property_name], 
                                        'value_total': j['lca_result'][property_name],
                                        'color': j['diagram_color'] }
        context['data_parts_property_bar_left'] =legend_dict


#    #doughnut diagram left concept
        output_Dict = {
            "labels": [],
            "datasets": [ ]
        }
        colours=[]
        for i in range(len(labels_left)):
            output_Dict["labels"].append(labels_left[i])
            colours.append(colors_left[i])

        output_Dict["datasets"].append({"data": data_left, "backgroundColor": colours, "borderColor": "#000000",  "borderWidth": 2 })
        context['data_parts_property_left_json'] =json.dumps(output_Dict, indent=4)

        #legend table
        legend_dict={}
        for i,j in analysis_left_sums['parts'].items():
            legend_dict[j['name']] = {'value_single': j['lca_part']['lca_result'][property_name], 
                                        'value_total': j['lca_result'][property_name],
                                        'color': j['diagram_color'] }
        context['data_parts_property_left'] =legend_dict


        #Find part with biggest CO2 impact
        CO2 = 0
        for part in analysis_left_sums['parts'].items():
            if CO2 < part[1]['lca_result']['carbon_footprint']:
                CO2 = part[1]['lca_result']['carbon_footprint']
        context['max_CO2_part'] = CO2
        #bar diagram comparison both concepts - left
        LCA_STEP_CHOICES = {} #this array will store Possible lca steps
        LCA_STEP_CHOICES = dict(Instance_Idemat_Database_Process.LCA_STEP_CHOICES)
        PROCESS_TYPE_CHOICES = {} #this array will store Possible lca steps
        PROCESS_TYPE_CHOICES = dict(Instance_Idemat_Database_Process.PROCESS_TYPE_CHOICES)
        output_Dict = {
            "labels": [],
            "datasets": []
        }

        labels=[]
        data={}        
        data_list=[]
        DATA_COUNT=len(entry)
        COUNTER=1

        part_number = len(analysis_left_sums['parts'])
        counter = 0
        for part in analysis_left_sums['parts'].items():
            output_Dict["labels"].append(part[1]['name']) 
            for step in LCA_STEP_CHOICES.items():
                for process_type in PROCESS_TYPE_CHOICES.items():
                    for process in analysis_left_sums['parts'][part[0]]['lca_part'][step[1]][process_type[1]].items():
                        if "ID" in process[0]: #we are checking if process is a process and not something else like lca_sum
                            data = [0] * part_number
                            data[counter] = process[1]['lca_result']['carbon_footprint'] * part[1]['multiplier']
                            output_Dict["datasets"].append({"label":process[1]['lca_input']['name'],
                                                        "data": data,
                                                        "backgroundColor": process[1]['color'],  
                                                        "borderColor": "#000000",   
                                                        "borderWidth": 2})
            counter +=1

        context['data_parts_processes_property_left_json'] =json.dumps(output_Dict, indent=4)

#########################################################################################################################

        # labels_left = []
        # data_left = []

        # colors_left =[]

        # for step in lca_parts_left_all:
        #     labels_left.append(step.part_model.name)
        #     data_left.append(step.part_model.weight)
        #     colors_left.append(step.color)


      
        # #BREAK EVEN POINT INDICATION
        # testdata_1 = []
        # testdata_2 = []

        # #get the first utilisation_process for visualisation (has to be extended in future versions
        # utilisation = current_analysis.utilisation_instance_model.first()
        # circularity_process = current_analysis.utilisation_instance_model.first()
        # if utilisation is not None:

        #     calc_interval = 1000 #calculation will be done for interval of 1000km
        #     nop = int(current_vehicle.life_distance_in_km /1000 +1) #+1 because of the startpoint so it has to be odd for
        #     x_pos = np.linspace(0,current_vehicle.life_distance_in_km, nop, endpoint = True).tolist()

        #     #penalty values for reuse of the part
        #     CO2bonusmalus_circularity_left = analysis_left_sums['lca_result_circularity']['carbon_footprint']
        #     #penalty values for manufacturing of the parts
        #     CO2bonusmalus_manufacturing_left = left_total_CO2



        #     #on the begining emmisions are generated only with manufacturing processes
        #     testdata_1.append(CO2bonusmalus_manufacturing_left)


        #     for i in range(nop-1):
        #         penalty_left = 0
        #         penalty_right = 0
        #         for lca_part in analysis_left.lca_part_models.all():
        #             if lca_part.circularity_process_model.check_bonusmalus(current_vehicle, i * calc_interval, calc_interval):
        #                 penalty_left +=  analysis_left_sums['parts'][lca_part.part_model.__str__()]['lca_result_circularity']['carbon_footprint']
            
            
        #         #for part in 
        #         testdata_1.append(testdata_1[i] + utilisation.engwpperkm_vehicle_for_analysis_left/100 * calc_interval + penalty_left)   #engwpperkm is for 100km

 #engwpperkm is for 100km

            # #line diagram 
            # output_Dict = {
            #     "labels": x_pos,
            #     "datasets": []
            # }

            # output_Dict["datasets"].append({"label":"Left Concept", "data":testdata_1, "fill": "false", "borderColor": "rgb(0, 255, 0)", "tension": 0.3 })	
    
            # context['break_even_point_utilisation_json'] =json.dumps(output_Dict, indent=4)

            # #identify break even point coordinates
            # test_n = False
            # test_n_1 = False
            # differences =  []
            # bep=None
            # for i in range(nop-1):
            #     differences.append(testdata_1[i] - testdata_2[i])

            # for i in range(nop-2):
            #     if (differences[i] <0 and differences[i+1] > 0) or (differences[i] >0 and differences[i+1] < 0) :
            #         bep = i
            #         break

            # if bep:
            #    context["break_even_point_X"] = int(x_pos[bep])
            #    context["break_even_point_Y"] = int(testdata_1[bep])
            # else:
            #    context["break_even_point_X"] = None
            #    context["break_even_point_Y"] = None
    

            # #set context for engwpperkm
            # context["engwpperkm_left"] =   utilisation.engwpperkm_vehicle_for_analysis_left * 1000 / 100
            # context["engwpperkm_right"] =  utilisation.engwpperkm_vehicle_for_analysis_right * 1000 / 100
            # context['Co2saving'] = int(testdata_1[nop-1]) - int(testdata_2[nop-1])
        return context