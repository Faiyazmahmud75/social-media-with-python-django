# Generated by Django 5.1.6 on 2025-02-24 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default/default.png', upload_to='profile_pics'),
        ),
    ]
