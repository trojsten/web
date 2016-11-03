from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import ExternalSubmitToken


class ExternalSubmitSerializer(serializers.Serializer):
    token = serializers.PrimaryKeyRelatedField(queryset=ExternalSubmitToken.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    points = serializers.DecimalField(max_digits=10, decimal_places=5)
