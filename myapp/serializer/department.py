from rest_framework import serializers
from ..model.department import Document, Department, Category, SubCategory
from ..models import User


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        #    fields=('user_id','email','username','is_active','is_admin')
        #    fields='__all__'
        exclude = ('password', 'last_login', 'is_superuser', 'groups', 'user_permissions')
