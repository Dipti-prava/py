from django.db import models


class Role(models.Model):
    role_id = models.CharField(max_length=5, primary_key=True)
    role_name = models.CharField(max_length=255)
    role_desc = models.TextField()


class Resource(models.Model):
    resource_id = models.CharField(max_length=5, primary_key=True)
    resource_name = models.CharField(max_length=255)
    resource_desc = models.TextField()


class RoleResourceMapping(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
