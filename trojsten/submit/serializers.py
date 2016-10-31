from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import ExternalSubmitKey


class ExternalSubmitSerializer(serializers.Serializer):
    key = serializers.PrimaryKeyRelatedField(queryset=ExternalSubmitKey.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    points = serializers.DecimalField(max_digits=10, decimal_places=5)
