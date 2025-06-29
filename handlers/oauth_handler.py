from google_auth_oauthlib.flow import Flow
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URI, SCOPES


class OAuthManager:
    def __init__(self):
        client_config = {
            'web': {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }

        self.flow = Flow.from_client_config(
            client_config=client_config,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )


    '''
    формирование ссылки для авторизации
    '''
    def get_auth_url(self):
        auth_url, state = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return auth_url, state

    '''
    полчуение токена в обмен на код, который клиент получил при авторизации
    '''
    def fetch_tokens(self, code: str):
        self.flow.fetch_token(code=code)
        return self.flow.credentials
