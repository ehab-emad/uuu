
#class info_concept(TemplateView):

#    def get_context_data(self, **kwargs):
#    # Call the base implementation first to get a context
#        context = super().get_context_data(**kwargs)
#        context['text'] = "Test text"      
#        return context
#    template_name = 'modals/info/info.html'
from django.template.loader import render_to_string
from django.http import JsonResponse
def info_concept(request):
    data = dict()
    context = {}
    template_name = 'modals/info/info.html'
  
    if request.POST['target']:
        context['target'] = request.POST['target']     
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

