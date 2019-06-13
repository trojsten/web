from social_core.backends.oauth import BaseOAuth2
from django.conf import settings


class TrojstenOAuth2(BaseOAuth2):
    name = "trojsten"
    ID_KEY = "id"
    AUTHORIZATION_URL = "%s/oauth/authorize/" % settings.TROJSTEN_LOGIN_PROVIDER_URL
    ACCESS_TOKEN_URL = "%s/oauth/token/" % settings.TROJSTEN_LOGIN_PROVIDER_URL
    USER_DATA_URL = "%s/api/me/" % settings.TROJSTEN_LOGIN_PROVIDER_URL
    ACCESS_TOKEN_METHOD = "POST"
    REDIRECT_STATE = False
    EXTRA_DATA = [("id", "id")]

    def get_user_details(self, response):
        """Return user details from Trojsten account"""
        fullname, first_name, last_name = self.get_user_names(response.get("display_name"))
        return {
            "id": str(response.get("id")),
            "username": str(response.get("username")),
            "email": response.get("email"),
            "fullname": fullname,
            "first_name": first_name,
            "last_name": last_name,
        }

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        return self.get_json(
            self.USER_DATA_URL, headers={"Authorization": "Bearer {0}".format(access_token)}
        )
