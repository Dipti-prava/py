# Generated by Django 3.2.4 on 2024-01-31 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_auto_20240131_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='sub_cat',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='myapp.subcategory'),
        ),
    ]
