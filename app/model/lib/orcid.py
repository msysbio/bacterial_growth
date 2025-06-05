"""
ORCID documentation:
https://info.orcid.org/documentation/api-tutorials/api-tutorial-get-and-authenticated-orcid-id/
"""

import os
import requests

APP_ENV = os.getenv("APP_ENV", "development")

if APP_ENV in ('development', 'test'):
    ORCID_ROOT_URL  = 'https://sandbox.orcid.org'
    ORCID_CLIENT_ID = 'APP-XM62M2OX6NY2F8JQ'
elif APP_ENV == 'production':
    ORCID_ROOT_URL  = 'https://orcid.org'
    ORCID_CLIENT_ID = 'APP-ULYLRC9LC29VYVBS'
else:
    raise ValueError(f"Unknown APP_ENV: {APP_ENV}")

def get_login_url(app_host):
    params = {
        'client_id':     ORCID_CLIENT_ID,
        'response_type': 'code',
        'scope':         'openid',
        'redirect_uri':  f"https://{app_host}/login/",
    }

    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])

    return f"{ORCID_ROOT_URL}/oauth/authorize?{query_string}"


def authenticate_user(code, secret, app_host):
    url = f"{ORCID_ROOT_URL}/oauth/token"
    data = {
        'client_id': ORCID_CLIENT_ID,
        'client_secret': secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': f"https://{app_host}/login/",
    }
    headers = {
        'Accept':       'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    r = requests.post(url, data=data, headers=headers)
    r.raise_for_status()

    return r.json()
