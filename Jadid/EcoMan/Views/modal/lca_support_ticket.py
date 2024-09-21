from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
#Please note that "idemat_process" should be renamed to "eco_process" as processes can be as well created from client


#idemat_process-----------------------------------------------------------------------------------
def lca_process_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
    #here fields deactivasted in the form will ba reactivated in order to be listed in cleaned_data to pass database Not-Null-Constraint
        form.fields["owner"].disabled = False
        form.fields["project_model"].disabled = False    
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True

            send_mail(
                "Ticket",
                "Hey it doesnt work!",
                "hubert.rybak@edag.com",
                ["qlca@edag.com"],
                fail_silently=False,
            )
            messages.add_message(request, messages.SUCCESS, "Ticket issued successfully")



        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def lca_support_ticket_create_modal(request):
    from EcoMan.forms import LcaSupportTicketForm
    if request.method == 'POST':
        form = LcaSupportTicketForm( request.POST, request = request)
    else:
        form = LcaSupportTicketForm(request = request)
    return lca_process_save_form(request, form, 'modals/lca_support_ticket/lca_support_ticket_create_modal.html')





