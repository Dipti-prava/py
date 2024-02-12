from django.db import models

from ..models import User
from ..utils.common import document_upload_path


class Department(models.Model):
    dep_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Category(models.Model):
    cat_name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    dep = models.ForeignKey(Department, on_delete=models.CASCADE)


class SubCategory(models.Model):
    sub_cat_name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    cat = models.ForeignKey(Category, on_delete=models.CASCADE)


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cat = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    sub_cat = models.ForeignKey(SubCategory, on_delete=models.CASCADE, default=2)
    name = models.CharField(max_length=255)
    doc = models.FileField(upload_to=document_upload_path)  # FileField for the uploaded document
    doc_type = models.CharField(max_length=100)
    size = models.IntegerField()
    upload_time = models.DateTimeField(auto_now_add=True)  # Timestamp of upload

    def __str__(self):
        return self.name
