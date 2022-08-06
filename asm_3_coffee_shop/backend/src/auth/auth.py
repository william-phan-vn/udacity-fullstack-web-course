import json
from http import HTTPStatus
from os import abort

from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'william-phan.jp.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://localhost:5000'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error_code: str, error_description: str, status_code: int):
        self.error_code = error_code
        self.description = error_description
        self.status_code = status_code


## Auth Header

'''
@DONE implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        raise AuthError(error_code='unauthorized',
                        error_description='Authorization header not found.',
                        status_code=401)
    header_parts = auth_header.split(' ')
    if len(header_parts) != 2 or header_parts[0].lower() != 'bearer':
        raise AuthError(error_code='unauthorized',
                        error_description='Header is malformed',
                        status_code=401)
    return header_parts[1]


'''
@DONE implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    permissions = payload.get('permissions')
    if permissions is None:
        raise AuthError(error_code='invalid_claims',
                        error_description='Permission not included in the token.',
                        status_code=400)

    if permission not in permissions:
        raise AuthError(error_code='unauthorized',
                        error_description='Permission not found.',
                        status_code=403)
    return True


'''
@DONE implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    # Get the public key from Auth0
    json_url = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(json_url.read())

#   Get the data in the header
    unverified_header = jwt.get_unverified_header(token)

#   Choose our key
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError('invalid_header', 'Authorization malformed', 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(token, rsa_key, algorithms=ALGORITHMS,
                                 audience=API_AUDIENCE, issuer=f'https://{AUTH0_DOMAIN}/')
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError(error_code='token_expired',
                            error_description='Token Expired.',
                            status_code=401)
        except jwt.JWTClaimsError:
            raise AuthError(error_code='invalid_claims',
                            error_description='Incorrect claims. Please check the audience and issuer.',
                            status_code=401)
        except Exception:
            raise AuthError(error_code='invalid_header',
                            error_description='Unable to parse authentication token.',
                            status_code=400)
    raise AuthError(error_code='invalid_header',
                    error_description='Unable to find the appropriate key.',
                    status_code=400)

'''
@DONE implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator