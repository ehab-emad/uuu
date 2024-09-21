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
        # 1. GROUPS PREPARATION
        # We need to allocate groups properly, there is need however to go through the groups 
        # recursively so that we can find proper ID to be then used in assignment below.
        group_ids = list()
        groups_to_be_assigned = [
            'be_paramount',
            'app-catiaframework',
            'app-conceptman',
            'app-ecoman',
            'app-boltman',
            'app-matman',
            'app-normman',
            'edag_worker',
            ]
        
        def check_for_subgroups(group_list: list):
            for subgroup in group_list:
                if subgroup['name'] in groups_to_be_assigned:
                    group_ids.append(subgroup['id'])
                if len(subgroup['subGroups']) > 0: 
                    check_for_subgroups(subgroup['subGroups'])

        groups = django_keycloak.user.get_groups()
        check_for_subgroups(groups)
        # here get group members
        group_context = dict()
        for group_id in group_ids:
            group_context[group_id] = [d['id'] for d in django_keycloak.user.get_group_members(group_id)]
        
        # 2. USERS PREPARATION
        # Here we try to get all users from keycloak and check for their attribute 
        # assignment, whether they have LDAP_ID, then this to be double checked if 
        # it is valid UUID. Afterwards, the user can get acces to applications.
        # There is a need to collect all the users declared by keycloak. This is to be 
        # done in 10 consecutive stepos as threshold for now        
        n_users = django_keycloak.user.users_count()
        threshold = 10
        for _ in range(threshold):
            users = django_keycloak.user.get_users()
            if len(users) == n_users:
                break

        # 3. INFORMATION ASSIGNMENT
        for user in users:
            if 'attributes' in user:
                if type(user['attributes']) is dict:
                    if 'LDAP_ID' in user['attributes'] and 'LDAP_ENTRY_DN' in user['attributes']:
                        # we have LDAP user, we cann add him to desired group
                        for group_id in group_context:
                            if user['id'] not in group_context[group_id]:                            
                                django_keycloak.user.group_user_add(user['id'], group_id)
                                print(f"User {user['id']} ({user['username']}) added to group {group_id}")