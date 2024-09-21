import time
from django.views.generic import  TemplateView
from django.shortcuts import redirect 
from django.http import JsonResponse
from website.models import ProjectUser
from website.settings import GROUPS


#from guest_user.decorators import allow_guest_user
from EcoMan.QLCA_Idemat_Calculation import *

def redirect_to_home(request):
    # Assuming you want to redirect from localhost:8000 to localhost:8000/home
    return redirect('/home')

class index(TemplateView):
    def get_context_data(self, **kwargs):        
        apps = list()
        if self.request.user:
            for group in GROUPS:
                if group in self.request.session.get('groups', '').split(','):
                    apps.append(f'website/applications/{GROUPS[group]}.html') if group in GROUPS else None                    
        c = super().get_context_data(**kwargs)                    
        c['apps'] = apps
        c['project_user'] = ProjectUser.objects.filter(user_id = self.request.user.pk) 
        c['user'] = self.request.user
        c['expiration_delay'] = self.request.session.get('expiration_delay', 60)
        c['expiration_timestamp'] = self.request.session.get('expiration_timestamp', int(time.time()))
        import_lca_constant('DIESEL','PETROL','SOMETHING')
        return c
    template_name = 'website/index.html'
