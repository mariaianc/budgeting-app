# Generated by Django 5.0.2 on 2024-04-24 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='achieved',
            field=models.BooleanField(default=False),
        ),
    ]
