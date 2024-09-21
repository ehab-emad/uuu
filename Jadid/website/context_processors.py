from website import settings
import django, platform, os
from website.models.organisation import Organisation
def environment_details(request):
   
    # Return a dictionary with your variable
    return {'BUILD_NUMBER': getattr(settings, 'BUILD_NUMBER', 'unknown'),
            'DATABASE_NAME': os.environ.get('DB_NAME', 'qlca_dev'),
            'DJANGO_DEBUG': getattr(settings, 'DEBUG', 'Unknown'),
            'DJANGO_VERSION': django.get_version(),
            'PYTHON_VERSION': platform.python_version(),
            'DEMO_VERSION_WATERMARK': getattr(settings, 'DEMO_VERSION_WATERMARK', False),
            'DEBUG_INFORMATION_SHOW': getattr(settings, 'DEBUG_INFORMATION_SHOW', False),
            'CURRENT_ORGANISATION': Organisation.get_current_organisation()
            }
