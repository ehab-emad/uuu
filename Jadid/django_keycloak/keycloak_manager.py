# import uuid
import time
from django.conf import settings
from django.contrib.auth import login, logout
from django.http import JsonResponse 
from django.shortcuts import redirect
from keycloak import KeycloakOpenID, KeycloakAdmin
from keycloak.exceptions import KeycloakAuthenticationError, KeycloakPostError
from urllib.parse import urlencode
from datetime import date, timedelta
from website.settings import FREE_USER_TRIAL_TIME_DAYS
from .auth import is_professional_user


EXCEPTIONS = (
    TypeError, 
    AttributeError, 
    KeyError, 
    KeycloakAuthenticationError, 
    KeycloakPostError
    )


class KeycloakManager():
    '''
    Create Keycloak instance
    -> This instance represents a connection to Keykloack OpenID client,
        which is in this case our be_paramount. For SSL error to terminate, simply by 
        changing verify to False, the server will not request a SSL verification and a 
        warning is raised: InsecureRequestWarning: Unverified HTTPS request is being made to host 
            'qlca.edag.de'. Adding certificate verification is strongly advised. 
            See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings  
            Depreciation does the thing and then is the communication possible.
    -> This should be only manager, not actual instance that is full of information, thus the 
        class is to be rebuilt regarding this concept. For that, the refresh token would be 
        communicated within request session so it would be also protected.
    '''

    def __init__(self):
        self.config = settings.KEYCLOAK_CONFIG
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
        self.redirect_uri = self.config.get('KEYCLOAK_REDIRECT_URI', None)
        self.keycloak = KeycloakOpenID(server_url=self.server_url,
                                       client_id=self.client_id,
                                       realm_name=self.realm,
                                       client_secret_key=self.client_secret_key,
                                       verify= False)  

    @staticmethod
    def get_or_create_user(user_info) -> object:
        from django.contrib.auth.models import User
        from website.models import ProjectUser
        username = user_info.get('preferred_username') or user_info.get('email')
        query = ProjectUser.objects.filter(keycloak_UUID=user_info['sub'])
        if query:
            user = query.get().user
            user.is_staff = 'qlca_staff' in user_info['roles']
            user.save()
        else:
            user = User(username = username)
            user.save()
            user.projectuser.keycloak_UUID = user_info['sub']
            user.projectuser.save()
        return user
    
    @staticmethod
    def update_user_expiration_date(user, groups):
        pu = user.projectuser
        if is_professional_user(groups):
            pu.expiration_date = None
            pu.save()
        elif pu.expiration_date == None:
            pu.expiration_date = date.today() + timedelta(days = FREE_USER_TRIAL_TIME_DAYS)
            pu.save()

    def introspect(self, token) -> dict:
        return self.keycloak.introspect(token=token)

    def refresh_token(self, refresh_token) -> dict|None:
        try:
            return self.keycloak.refresh_token(refresh_token) 
        except EXCEPTIONS:
            return None
        
    def get_expiration_timestamp(self, refresh_token) -> str:
        try:
            current_token = self.refresh_token(refresh_token)
            return int(time.time()) + current_token['refresh_expires_in']
        except EXCEPTIONS:
            int(time.time())
            
    def is_user_logged_in(self, refresh_token) -> bool:
        try:
            current_token = self.refresh_token(refresh_token)
            user_info = self.keycloak.userinfo(current_token['access_token'])
            status = True if user_info is not None else False
            return status
        except EXCEPTIONS:
            return False

    def get_token(self, request) -> dict:
        # -> uri has to be programatically defined
        return self.keycloak.token(grant_type='authorization_code', code=request.GET['code'], redirect_uri=self.redirect_uri)
    
    def keycloak_login(self, request) -> any:
        current_token = self.get_token(request)
        user_info = self.keycloak.userinfo(current_token['access_token']) 
        user = self.get_or_create_user(user_info)

        # from django.template.response import TemplateResponse
        # import jwt
        # import requests

        # access_token = current_token['access_token']
        # csrf_token = TemplateResponse(request, "NormMan//get_csrf_token.html", {}).rendered_content.split('"')[-2]
        # headers = {
        #     "Authorization": f"Bearer {access_token}",
        #     "Content-Type": "application/json",
        #     "X-CSRF-Token": csrf_token
        # }
        # attr = {
        #     'attributes': {
        #         'test_attribute': 'test'
        #     }
        # }

        # decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        # user_id = decoded_token['sub']
        # url = f"{self.server_url}/admin/realms/{self.realm}/users/{user_id}/groups/be_paramount/app-boltman"
        # url = f"{self.server_url}/admin/realms/{self.realm}/users/{user_id}"
        # response = requests.put(url, json=attr, headers=headers)
        # response = requests.put(url, headers=headers)


        login(request, user)
        groups = user_info.get('groups', [])
        self.update_user_expiration_date(user, groups)
        request.session['groups'] = ','.join(groups)
        request.session['roles'] = ','.join(user_info['roles'])
        request.session['expiration_timestamp'] = int(time.time()) + current_token['refresh_expires_in']
        request.session['expiration_delay'] = current_token['refresh_expires_in']
        request.session['refresh_token'] = current_token['refresh_token']
        response = redirect('/')
        return response
    
    def expired_login(self, request) -> any:
        try:
            current_token = self.refresh_token(request.session['refresh_token'])
            if current_token:
                self.keycloak.logout(current_token['refresh_token'])
        except EXCEPTIONS:
            pass
        logout(request)
        return JsonResponse(dict(), status=200)
    
    def keycloak_logout(self, request) -> any:
        try:            
            current_token = self.refresh_token(request.session['refresh_token'])
            if current_token:
                self.keycloak.logout(current_token['refresh_token'])        
        except EXCEPTIONS:
            pass
        logout(request)
        return redirect('/')
        
    def keycloak_admin_redirect(self, request) -> any:
        self.redirect_uri = f"{request.scheme}://{request.headers['Host']}{self.config.get('KEYCLOAK_REDIRECT_URI', None)}"        
        authorize_url = f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/auth"
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'openid',
        }
        redirect_url = f"{authorize_url}?{urlencode(params)}"    
        return redirect(redirect_url)
    
    def user_login(self, username:str, password:str):
        self.user = KeycloakAdmin(server_url=self.server_url,
                        username=username,
                        password=password,
                        realm_name=self.realm,
                        verify=False)
#ff
        
keycloak_manager = KeycloakManager()
