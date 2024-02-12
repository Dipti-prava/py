from rest_framework import serializers

from ..model.admin import Role, Resource, RoleResourceMapping


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'


class RoleResourceMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleResourceMapping
        fields = '__all__'
