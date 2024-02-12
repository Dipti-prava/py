from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from .models import Grievance


class GrievanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grievance
        exclude = ['gk_id']
        # fields =  ('id', 'user', 'title', 'description')


class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['username'] = user.username
        data['userid'] = user.id
        data['email'] = user.email
        return data
