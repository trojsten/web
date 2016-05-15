from django.http import JsonResponse
from oauth2_provider.views.generic import ProtectedResourceView

class CurrentUserInfo(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        user = request.user
        user_info = {
            'uid': user.username,
        }
        return JsonResponse(user_info)
