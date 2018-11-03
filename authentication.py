#!/home/syrup/anaconda3/envs/etsy3/bin/python

from etsy_py.api import EtsyAPI
from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1
import requests
import pickle

def have_req_permissions(api, auth, req_permissions_set):
    '''checks the current authentication's permissions through the etsy api.
    If we have everything in the req_permissions_set, return true, otherwise
    return false'''
    r = api.get("/oauth/scopes", auth=auth)    
    permissions = r.json()['results']
    permission_dict = {}
    for perm in permissions:
        permission_dict[perm] = "yep"
    for req in req_permissions_set:
        if req not in permission_dict:
            print(f"Current Authentication missing {req} permissions!")
            return False
    return True

def get_oauth_file():
    file_name = f'oauth/my_token.secret'
    return file_name

def get_oauth(api, api_key, client_secret, req_permission_set):
   
    oauth_file = get_oauth_file()
    try:
        with open(oauth_file, 'rb') as fh:
            token = pickle.load(fh)
    except:
        print("Could not find local authentication token! Will request one")
        token = get_new_oauth_access_token(api_key,
                                           client_secret,
                                           req_permission_set)
        # pickle the oauth file
        with open(oauth_file, 'wb') as fh:
            pickle.dump(token, fh)

    rok = token.get('oauth_token')
    ros = token.get('oauth_token_secret')
    auth = OAuth1(api_key, client_secret, rok, ros)
    if not have_req_permissions(api, auth, req_permission_set):
        token = pickle_new_oauth_token(oauth_file,
                                       api_key,
                                       client_secret,
                                       req_permission_set)
        rok = token.get('oauth_token')
        ros = token.get('oauth_token_secret')
        auth = OAuth1(api_key, client_secret, rok, ros)
    return auth

def get_new_oauth_access_token(api_key, client_secret, req_permission_set):
    # OAuth authentication
    oauth = OAuth1Session(api_key, client_secret=client_secret)
    request_token_url = 'https://openapi.etsy.com/v2/oauth/request_token'
    permissions = "%20".join(req_permission_set)
    if permissions != "":
        permissions = "?scope=" + permissions
    request_token_url += permissions
    oauth_r = oauth.fetch_request_token(request_token_url)
    resource_owner_key = oauth_r.get('oauth_token')
    resource_owner_secret = oauth_r.get('oauth_token_secret')
    auth_url = oauth_r.get('login_url')

    print(f"""

        1. Go to <{auth_url}>
        2. Login if necessary
        3. Click on "Allow Access"
        4. Enter the verification code given

    """)

    verifier = input("Input the verification code : ")

    access_token_url = 'https://openapi.etsy.com/v2/oauth/access_token'
    oauth = OAuth1Session(api_key, 
                          client_secret=client_secret,
                          resource_owner_key=resource_owner_key,
                          resource_owner_secret=resource_owner_secret,
                          verifier=verifier)

    oauth_token = oauth.fetch_access_token(access_token_url)
    # resource_owner_key = oauth_tokens.get('oauth_token')
    # resource_owner_secret = oauth_tokens.get('oauth_token_secret')
    return oauth_token

