# Generated by Django 3.2.4 on 2024-02-09 11:19

from django.db import migrations, models
import myapp.utils.common


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_document_sub_cat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_no',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_pic',
            field=models.FileField(upload_to=myapp.utils.common.document_upload_path),
        ),
    ]
