from typing import Callable, Mapping, Sequence, Optional, Any
import functools
import re
import json
from requests_oauthlib import OAuth2Session
import secrets

MAL_CLIENT_ID='531e6940ede6724ca1a08c41d9e1f1a3'
MAL_CLIENT_SECRET='8f5cbd5083fb0c3bd6356672cd2c535addd55053ddac3d83a81271056f67dac1'

class Shikimori:
    SHIKIMORI_URL: str = 'https://myanimelist.net'
    _TOKEN_URL = SHIKIMORI_URL + '/v1/oauth2/token'
    API_URL='https://api.myanimelist.net/v2'
    def __init__(self,
                 app_name:      Optional[str] = None,
                 *,
                 client_id:     Optional[str] = None,
                 client_secret: Optional[str] = None,
                 token:         Optional[Mapping] = None,
                 redirect_uri:  str = 'http://127.0.0.1:8000',
                 token_saver:   Optional[Callable[[dict], Any]] = None,
                 scope:         Optional[Sequence[str]] = None
                 ) -> None:
        self.code_verifier = self.code_challenge = self.get_new_code_verifier()
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_saver = token_saver or (lambda d: None)
        self._headers = {
            'User-Agent': app_name,
        }
        self._extra = {
            'response_type':'code',
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'code_challenge':self.code_challenge,

        }
        self._client = self._get_client(scope, redirect_uri, token)

    def _get_client(self, scope, redirect_uri, token):
        client = OAuth2Session(self._client_id, auto_refresh_url=self._TOKEN_URL, auto_refresh_kwargs=self._extra,
                               scope=scope, redirect_uri=redirect_uri, token=token, token_updater=self._token_saver)
        client.headers.update(self._headers)
        return client
    def get_new_code_verifier(self) -> str:
        token = secrets.token_urlsafe(100)
        return token[:128]


    def get_auth_url(self) -> str:
        auth_url = self.SHIKIMORI_URL + '/v1/oauth2/authorize'
        return self._client.authorization_url(auth_url,code_challenge=self.code_challenge)[0]

    def fetch_token(self, code: str) -> dict:
        self._client.fetch_token(self._TOKEN_URL, code=code,code_verifier=self.code_verifier,client_id=self._client_id, client_secret=self._client_secret)
        self._token_saver(self.token)
        return self.token

    @property
    def token(self) -> dict:
        return self._client.token

    def request(self, method: str, path: str, **params):
        url = self._get_request_url(path)
        kwargs = {'params': params} if method == 'GET' else {'json': params}
        response = self._client.request(method, url, **kwargs)

        if response.ok:
            return response.json()
        response.raise_for_status()

    def _get_request_url(self, path):

        return self.API_URL + path 

    def get_api(self) -> 'ApiMethod':
        return ApiMethod(self)


class ApiMethod:
    _HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

    def __init__(self, session: Shikimori, path: str = '') -> None:
        self._session = session
        self._path = path

    def __call__(self, item) -> 'ApiMethod':  # item: SupportsStr
        new_path = self._path + '/' + str(item)
        return ApiMethod(self._session, new_path)

    def __getattr__(self, item) -> 'ApiMethod':
        if item in self._HTTP_METHODS:
            return functools.partial(self._session.request, item, self._path)
        new_path = self._path + '/' + item
        return ApiMethod(self._session, new_path)
def token_saver(token: dict):
    with open('mal_token.json', 'w') as f:
        f.write(json.dumps(token))
def regis():
    session = Shikimori('web',
                        client_id=MAL_CLIENT_ID,
                        client_secret=MAL_CLIENT_SECRET,
                        token_saver=token_saver)

    url=session.get_auth_url()
    print(url)
    code = input('Authorization Code: ')
    a=session.fetch_token(code)

    api = session.get_api()
def log():
    with open('titles/api_urls/mal_token.json') as f:
        token = json.load(f)

    session = Shikimori('web',
                        client_id=MAL_CLIENT_ID,
                        client_secret=MAL_CLIENT_SECRET,
                        token_saver=token_saver,
                        token=token)
    api = session.get_api()
    return api
