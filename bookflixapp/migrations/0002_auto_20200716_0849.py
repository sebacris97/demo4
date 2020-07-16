# Generated by Django 3.0.7 on 2020-07-16 11:49

import bookflixapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookflixapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='libro',
            name='trailer',
        ),
        migrations.AddField(
            model_name='libro',
            name='imagen',
            field=models.ImageField(default='default.jpg', null=True, upload_to=bookflixapp.models.Libro.content_file_name, verbose_name='Imagen'),
        ),
        migrations.AddField(
            model_name='libro',
            name='texto',
            field=models.TextField(default='NONE', max_length=1000, verbose_name='Texto'),
        ),
    ]