from social.backends.oauth import BaseOAuth2


class TrojstenOAuth2(BaseOAuth2):
    name = 'trojsten'
    ID_KEY = 'uid'
    # @TODO: replace with:
    # AUTHORIZATION_URL = 'https://login.trojsten.sk/oauth/authorize'
    # ACCESS_TOKEN_URL = 'https://login.trojsten.sk/oauth/token'
    AUTHORIZATION_URL = 'https://localhost:8000/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://localhost:8000/oauth/token'
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
        return {'username': str(response.get('uid')),
                'email': response.get('email'),
                'fullname': fullname,
                'first_name': first_name,
                'last_name': last_name}

    # def user_data(self, access_token, *args, **kwargs):
    #     """Loads user data from service"""
    #     return self.get_json(
    #         'https://login.trojsten.sk/ucet/',
    #         headers={'Authorization': 'Bearer {0}'.format(access_token)}
    #     )
