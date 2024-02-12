# Generated by Django 3.2.4 on 2024-01-09 11:16

from django.db import migrations, models
import myapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_user_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_no',
            field=models.CharField(default='8917247372', max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_pic',
            field=models.FileField(default='documents/images/my_img.jpeg', upload_to=myapp.models.document_upload_path),
        ),
    ]