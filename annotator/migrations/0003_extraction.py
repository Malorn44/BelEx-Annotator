# Generated by Django 3.0.7 on 2020-06-17 18:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0002_annotation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Extraction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ext_text', models.CharField(max_length=1000)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotator.Entry')),
            ],
        ),
    ]
