# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Marcos Pereira <marcospereira.mpj@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from keycloak import KeycloakOpenID, KeycloakAdmin
from keycloak.exceptions import KeycloakInvalidTokenError
from website.models import ProjectUser
import uuid
# from rest_framework.exceptions import PermissionDenied, AuthenticationFailed, NotAuthenticated


from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from keycloak import KeycloakOpenID
 
def keycloak_callback(request):
    # Set up Keycloak client configuration
    config = settings.KEYCLOAK_CONFIG

    # Read configurations
    try:
        server_url = config['KEYCLOAK_SERVER_URL']
        client_id = config['KEYCLOAK_CLIENT_ID']
        realm = config['KEYCLOAK_REALM']
    except KeyError as e:
        raise Exception("KEYCLOAK_SERVER_URL, KEYCLOAK_CLIENT_ID or KEYCLOAK_REALM not found.")

    client_secret_key = config.get('KEYCLOAK_CLIENT_SECRET_KEY', None)
    client_public_key = config.get('KEYCLOAK_CLIENT_PUBLIC_KEY', None)
    default_access = config.get('KEYCLOAK_DEFAULT_ACCESS', "DENY")
    method_validate_token = config.get('KEYCLOAK_METHOD_VALIDATE_TOKEN', "INTROSPECT")
    keycloak_authorization_config = config.get('KEYCLOAK_AUTHORIZATION_CONFIG', None)

    # Create Keycloak instance
    # -> This instance represents a connection to Keykloack OpenID client,
    #   which is in this case our be_paramount. For SSL error to terminate, simply by 
    #   changing verify to False, the server will not request a SSL verification and a 
    #   warning is raised: InsecureRequestWarning: Unverified HTTPS request is being made to host 
    #       'qlca.edag.de'. Adding certificate verification is strongly advised. 
    #       See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings  
    #   Depreciation does the thing and then is the communication possible.
    keycloak = KeycloakOpenID(server_url=server_url,
                                    client_id=client_id,
                                    realm_name=realm,
                                    client_secret_key=client_secret_key,
                                    verify= False)
    token = keycloak.token(grant_type='authorization_code', code=request.GET['code'], redirect_uri="http://127.0.0.1:8000/keycloak/login/callback/")


    # Extract user information from the token
    user_info = keycloak.userinfo(token['access_token'])
 
    # Perform Django user login based on user_info
    # You need to implement a function to create or update the Django user
    user = get_or_create_user(user_info)
 
    # Log in the user
    login(request, user)
 
    return redirect('/')  # Redirect to the desired Django page after successful login
 
def get_or_create_user(user_info):
    # Implement logic to get or create a Django user based on Keycloak user_info
    # Example: You might use the email or username from Keycloak to identify the user
    username = user_info.get('preferred_username') or user_info.get('email')
 
    # Use the Django User model or your custom User model  
    query = ProjectUser.objects.filter(UUID= user_info['sub'])
    if query:
        user = query.get().user
    else:
        user = User() #.objects.create(username=username)
        user.username = username
        user.temp_uuid = uuid.UUID(user_info['sub'])
        user.save()        
    user.projectuser.UUID = uuid.UUID(user_info['sub'])
    user.save()

 
    # if created:
    #     # Set additional user attributes if needed
    #     # user.first_name = user_info.get('given_name', '')
    #     # user.last_name = user_info.get('family_name', '')
    #     user.save()
 
    return user

def keycloak_logout(request):
    config = settings.KEYCLOAK_CONFIG

    # Read configurations
    try:
        server_url = config['KEYCLOAK_SERVER_URL']
        client_id = config['KEYCLOAK_CLIENT_ID']
        realm = config['KEYCLOAK_REALM']
    except KeyError as e:
        raise Exception("KEYCLOAK_SERVER_URL, KEYCLOAK_CLIENT_ID or KEYCLOAK_REALM not found.")

    client_secret_key = config.get('KEYCLOAK_CLIENT_SECRET_KEY', None)
    client_public_key = config.get('KEYCLOAK_CLIENT_PUBLIC_KEY', None)
    default_access = config.get('KEYCLOAK_DEFAULT_ACCESS', "DENY")
    method_validate_token = config.get('KEYCLOAK_METHOD_VALIDATE_TOKEN', "INTROSPECT")
    keycloak_authorization_config = config.get('KEYCLOAK_AUTHORIZATION_CONFIG', None)

    # Create Keycloak instance
    # -> This instance represents a connection to Keykloack OpenID client,
    #   which is in this case our be_paramount. For SSL error to terminate, simply by 
    #   changing verify to False, the server will not request a SSL verification and a 
    #   warning is raised: InsecureRequestWarning: Unverified HTTPS request is being made to host 
    #       'qlca.edag.de'. Adding certificate verification is strongly advised. 
    #       See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings  
    #   Depreciation does the thing and then is the communication possible.
    keycloak = KeycloakOpenID(server_url=server_url,
                                    client_id=client_id,
                                    realm_name=realm,
                                    client_secret_key=client_secret_key,
                                    verify= False)
    user_id = request.user.projectuser.UUID
    logout(request)

    return redirect('/')


class KeycloakMiddleware():

    def __init__(self): #, get_response):
        """

        :param get_response:
        """
        # self.get_response = get_response

        self.config = settings.KEYCLOAK_CONFIG

        # Read configurations
        try:
            self.server_url = self.config['KEYCLOAK_SERVER_URL']
            self.client_id = self.config['KEYCLOAK_CLIENT_ID']
            self.realm = self.config['KEYCLOAK_REALM']
        except KeyError as e:
            raise Exception("KEYCLOAK_SERVER_URL, KEYCLOAK_CLIENT_ID or KEYCLOAK_REALM not found.")

        self.client_secret_key = self.config.get('KEYCLOAK_CLIENT_SECRET_KEY', None)
        self.client_public_key = self.config.get('KEYCLOAK_CLIENT_PUBLIC_KEY', None)
        self.default_access = self.config.get('KEYCLOAK_DEFAULT_ACCESS', "DENY")
        self.method_validate_token = self.config.get('KEYCLOAK_METHOD_VALIDATE_TOKEN', "INTROSPECT")
        self.keycloak_authorization_config = self.config.get('KEYCLOAK_AUTHORIZATION_CONFIG', None)

        # Create Keycloak instance
        # -> This instance represents a connection to Keykloack OpenID client,
        #   which is in this case our be_paramount. For SSL error to terminate, simply by 
        #   changing verify to False, the server will not request a SSL verification and a 
        #   warning is raised: InsecureRequestWarning: Unverified HTTPS request is being made to host 
        #       'qlca.edag.de'. Adding certificate verification is strongly advised. 
        #       See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings  
        #   Depreciation does the thing and then is the communication possible.
        self._keycloak = KeycloakOpenID(server_url=self.server_url,
                                       client_id=self.client_id,
                                       realm_name=self.realm,
                                       client_secret_key=self.client_secret_key,
                                       verify= False)
        # Then a connection is established and we can access all the features of Keykloack, as we 
        # communicate directly with it.
        pass
    
    
    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response
    
    
    def login(self, username:str, password:str):
        self.user = KeycloakAdmin(server_url=self.server_url,
                        username=username,
                        password=password,
                        realm_name=self.realm,
                        verify=False)
            
    def get_token(self, request) -> dict:
        # -> uri has to be programatically defined
        self.token = self.keycloak.token(grant_type='authorization_code', code=request.GET['code'], redirect_uri="http://127.0.0.1:8000/keycloak/login/callback/")
        return self.token
    
    @property
    def token(self) -> dict:
        return self._token

    @token.setter
    def token(self, value):        
        self._token = value

    @property
    def userinfo(self) -> dict:
        return self.keycloak.userinfo(self.token['access_token'])
    
    @staticmethod
    def get_or_create_user(user_info) -> User:
        username = user_info.get('preferred_username') or user_info.get('email')
        query = ProjectUser.objects.filter(UUID= user_info['sub'])
        if query:
            user = query.get().user
        else:
            user = User()
            user.username = username
            user.temp_uuid = uuid.UUID(user_info['sub'])
        user.save()
        return user
    
    def keycloak_login(self, request):
        self.get_token(request)
        user = self.get_or_create_user(self.userinfo)
        login(request, user)    
        return redirect('/')
    
    def keycloak_logout(self, request):
        self.keycloak.logout(self.token['refresh_token'])
        logout(request)        
        return redirect('/')




    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):        
        self._user = value

    @property
    def keycloak(self):
        return self._keycloak

    @keycloak.setter
    def keycloak(self, value):
        self._keycloak = value

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def server_url(self):
        return self._server_url

    @server_url.setter
    def server_url(self, value):
        self._server_url = value

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, value):
        self._client_id = value

    @property
    def client_secret_key(self):
        return self._client_secret_key

    @client_secret_key.setter
    def client_secret_key(self, value):
        self._client_secret_key = value

    @property
    def client_public_key(self):
        return self._client_public_key

    @client_public_key.setter
    def client_public_key(self, value):
        self._client_public_key = value

    @property
    def realm(self):
        return self._realm

    @realm.setter
    def realm(self, value):
        self._realm = value

    @property
    def keycloak_authorization_config(self):
        return self._keycloak_authorization_config

    @keycloak_authorization_config.setter
    def keycloak_authorization_config(self, value):
        self._keycloak_authorization_config = value

    @property
    def method_validate_token(self):
        return self._method_validate_token

    @method_validate_token.setter
    def method_validate_token(self, value):
        self._method_validate_token = value

    def __call__(self, request):
        """

        :param request:
        :return:
        """
        return self.get_response(request)

    # def process_view(self, request, view_func, view_args, view_kwargs):
    #     """

    #     Validate only the token introspect.

    #     :param request: django request
    #     :param view_func:
    #     :param view_args: view args
    #     :param view_kwargs: view kwargs
    #     :return:
    #     """

    #     try:
    #         view_scopes = view_func.view_class.keycloak_scopes
    #     except AttributeError as e:
    #         raise Exception("Scopes mappers not found.")

    #     if 'HTTP_AUTHORIZATION' not in request.META:
    #         return JsonResponse({"detail": NotAuthenticated.default_detail},
    #                             status=NotAuthenticated.status_code)

    #     token = request.META.get('HTTP_AUTHORIZATION')

    #     # Get default if method is not defined.
    #     required_scope = view_scopes.get(request.method, None) \
    #         if view_scopes.get(request.method, None) else view_scopes.get('DEFAULT', None)

    #     # DEFAULT scope not found and DEFAULT_ACCESS is DENY
    #     if not required_scope and self.default_access == 'DENY':
    #         return JsonResponse({"detail": PermissionDenied.default_detail},
    #                             status=PermissionDenied.status_code)

    #     try:
    #         user_permissions = self.keycloak.get_permissions(token,
    #                                                          method_token_info=self.method_validate_token.lower(),
    #                                                          key=self.client_public_key)
    #     except KeycloakInvalidTokenError as e:
    #         return JsonResponse({"detail": AuthenticationFailed.default_detail},
    #                             status=AuthenticationFailed.status_code)

    #     for perm in user_permissions:
    #         if required_scope in perm.scopes:
    #             return None

    #     # User Permission Denied
    #     return JsonResponse({"detail": PermissionDenied.default_detail},
    #                         status=PermissionDenied.status_code)
