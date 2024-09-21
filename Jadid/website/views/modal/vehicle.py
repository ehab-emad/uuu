from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from website.forms import VehicleForm
from website.models import Vehicle
#Vehicle-----------------------------------------------------------------------------------

def vehicle_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            new_vehicle =form.save()
            new_vehicle.user=request.user
            new_vehicle.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
    else:
        form = VehicleForm()
    return vehicle_save_form(request, form, 'modals/vehicle/vehicle_create_modal.html')

def vehicle_update(request, uuid):
    car = get_object_or_404(Vehicle, pk=uuid)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=car)
    else:
        form = VehicleForm( instance=car)
    return vehicle_save_form(request, form, 'modals/vehicle/vehicle_update_modal.html')

def vehicle_delete(request, uuid):
    vehicle = get_object_or_404(Vehicle, pk=uuid)
    data = dict()
    if request.method == 'POST':
        vehicle.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        vehicles = Vehicle.objects.all()
        data['html_vehicle_list'] = render_to_string('BoltMan/vehicle_cards.html', {
            'vehicles': vehicles
        })
    else:
        context = {'vehicle': vehicle}
        data['html_form'] = render_to_string('modals/vehicle/vehicle_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)