# Generated by Django 3.0.7 on 2020-06-25 00:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0007_annotation_editing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annotation',
            name='editing',
        ),
    ]
