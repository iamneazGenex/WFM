# Generated by Django 4.2.6 on 2024-02-28 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0009_loginlogouttime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginlogouttime',
            name='logout_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='loginlogouttime',
            name='logout_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
