import os, json
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils.html import format_html
from NormMan.models import Component_Group_Level, NormParts_Shared_Component
from CatiaFramework.models import Workflow_Object
from website.settings import BASE_DIR, MEDIA_ROOT
from . import shared_component_dynamic_breadcrumb_modal


def shared_component_select(request, object_id, instance_id):
    from CatiaFramework.forms import SharedComponentSelectorForm
    group_level = Component_Group_Level.objects.filter(group_depth_level = 0).first()
    form = SharedComponentSelectorForm(request.user.projectuser.current_project_id, level = group_level)
    context = {
        'form': form,
        'category_group': group_level,
        'category_groups': Component_Group_Level.objects.filter(parent_group__UUID = group_level.UUID),
        'norm_parts_collector': form.norm_parts_collector,
        'html_dynamic_breadcrumb': format_html(shared_component_dynamic_breadcrumb_modal(group_level)),
        'object_id': object_id,
        'instance_id': instance_id
        }
    data = {
        'form_is_valid': True if request.method == 'POST' else False,
        'html_form': render_to_string('modals/shared_component/archiv/shared_component_select.html', context, request=request)
    }
    return JsonResponse(data)


def shared_component_reload(request):
    from CatiaFramework.forms import SharedComponentConfiguration
    group_level = Component_Group_Level.objects.filter(UUID = request.GET['category_id']).get()
    context_category_groups = {
        'category_group': group_level,
        'category_groups': Component_Group_Level.objects.filter(parent_group__UUID = request.GET['category_id']),
        'html_dynamic_breadcrumb': format_html(shared_component_dynamic_breadcrumb_modal(group_level)),
    }
    context = {
        'norm_parts_collector': [SharedComponentConfiguration(meta = obj) for obj in group_level.normparts_shared_components.all()],
        }
    data = {
        'html_category_groups': render_to_string('modals/shared_component/archiv/shared_component_group_cards.html', context_category_groups, request=request),
        'html_norm_parts_collector': render_to_string('modals/shared_component/archiv/shared_component_table.html', context, request=request)
    }
    return JsonResponse(data)


def shared_component_propagate(request):    
    # so we return then probably only rendered picture of modified object
    query_instance = Workflow_Object.objects.filter(UUID=request.POST['instance_id'])
    query_shared_component = NormParts_Shared_Component.objects.filter(UUID=request.POST['norm_part_uuid'])
    if query_instance and query_shared_component:
        instance, shared_component = query_instance.get(), query_shared_component.get()
        # instance.thumbnail = shared_component.thumbnail
        # instance.save()
    response = f'<img class="card-img-left" src="{shared_component.thumbnail.url}" style="height: 7rem; object-fit: contain;"/>'
    return JsonResponse({'image': response})



