from django.apps import AppConfig
from django_keycloak.keycloak_manager import KeycloakManager
from django.core.management import call_command
from decouple import config
from django.conf import settings
import os
from django.contrib.staticfiles.storage import staticfiles_storage
class websiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'
    verbose_name = 'Home of a Hell'

    def ready(self):
        from website.models import Organisation  # Import here to avoid issues during startup
        query = Organisation.objects.filter(name = 'EDAG')
        if not query:
            Organisation.objects.create(name = os.environ.get('DJANGO_CUSTOMER_SHORT_NAME', config('DJANGO_CUSTOMER_SHORT_NAME', default='EDAG')), 
                                        full_name = os.environ.get('DJANGO_CUSTOMER_FULL_NAME', config('DJANGO_CUSTOMER_FULL_NAME', default='EDAG Engineering GmbH')), 
                                        is_current_organisation=True
                                        )




class DashboardConfig(AppConfig):
    name = 'dashboard'
    default = False