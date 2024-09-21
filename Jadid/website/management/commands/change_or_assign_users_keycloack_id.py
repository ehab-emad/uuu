import uuid
from getpass import getpass
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django_keycloak.keycloak_manager import KeycloakManager
from website.models import ProjectUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        django_keycloak = KeycloakManager()
        django_keycloak.user_login(
            username=input("Insert admin user creadentials: "), 
            password=getpass("Insert admin user password: ")
            )
        for user in User.objects.all():
            print(f'User {user.username} is being analyzed.')
            try:
                user.projectuser
                has_project_user = True
                print(f' - associated ProjectUser found')
            except KeyError as e:
                has_project_user = False                 
            user_id = django_keycloak.user.get_user_id(user.username)
            print(f' - associated Keycloak User with ID {user_id} found')
            if user_id:
                # User does exist in keycloak
                if has_project_user:
                    print(' - updating ProjectUser...')
                    # User has Projectuser and thus can be updated
                    user.projectuser.keycloak_UUID = uuid.UUID(user_id)
                    pass
                else:
                    # User exists in keycloak but has no Projectuser assigned to it. Thus, it is created.
                    print(' - creating ProjectUser...')
                    user.projectuser = ProjectUser.objects.create(keycloak_UUID = uuid.UUID(user_id))
                print(' - saving...')
                user.save()
                print('Done!')
            else:
                # User does not exist in keycloak, Django User can be therefore removed or no action takes place.
                if False:
                    # This is a part for deleting not used users, which have non
                    # complete definition without properly configured projectuser
                    # instance. This will be deprecated in future with simple False
                    # in this condition
                    user.delete()
                else:
                    continue