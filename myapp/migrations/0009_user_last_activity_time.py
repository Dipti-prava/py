# Generated by Django 3.2.4 on 2024-01-11 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_document_cat'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_activity_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]