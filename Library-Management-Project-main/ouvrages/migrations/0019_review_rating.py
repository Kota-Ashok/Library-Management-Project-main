# Generated by Django 5.0.4 on 2024-05-19 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ouvrages', '0018_alter_exemplaire_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='rating',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
