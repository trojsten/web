from social.backends.oauth import BaseOAuth2


class TrojstenOAuth2(BaseOAuth2):
    name = 'trojsten'
    ID_KEY = 'uid'
    AUTHORIZATION_URL = 'https://login.trojsten.sk/oauth/authorize/'
    ACCESS_TOKEN_URL = 'https://login.trojsten.sk/oauth/token/'
    USER_DATA_URL = 'https://login.trojsten.sk/api/me/'
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    EXTRA_DATA = [
        ('uid', 'username'),
    ]

    def get_user_details(self, response):
        """Return user details from Trojsten account"""
        fullname, first_name, last_name = self.get_user_names(
            response.get('display_name')
        )
        print(response)
        return {
            'username': str(response.get('uid')),
            'email': response.get('email'),
            'fullname': fullname,
            'first_name': first_name,
            'last_name': last_name,
        }

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        return self.get_json(
            self.USER_DATA_URL,
            headers={'Authorization': 'Bearer {0}'.format(access_token)}
        )


class TrojstenLocalOAuth2(TrojstenOAuth2):
    name = 'trojsten_local'
    AUTHORIZATION_URL = 'http://localhost:8047/oauth/authorize/'
    ACCESS_TOKEN_URL = 'http://localhost:8047/oauth/token/'
    USER_DATA_URL = 'http://localhost:8047/api/me/'

