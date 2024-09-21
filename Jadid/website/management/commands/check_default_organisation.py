# your_app_name/management/commands/check_default_organisation.py

from django.core.management.base import BaseCommand
from website.models import Organisation

class Command(BaseCommand):
    help = 'Checks if a default organisation exists and creates one if it does not'

    def handle(self, *args, **kwargs):
        if not Organisation.objects.exists():
            Organisation.objects.create(name="Default Organisation", is_current_organisation=True)
            self.stdout.write(self.style.SUCCESS('Default organisation created.'))
        else:
            self.stdout.write(self.style.SUCCESS('Organisation already exists.'))
