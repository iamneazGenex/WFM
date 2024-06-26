# Generated by Django 4.2.6 on 2024-05-29 06:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('roster', '0033_alter_roster_shiftlegend'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roster',
            name='supervisor_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rosterSupervisor1', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='roster',
            name='supervisor_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rosterSupervisor2', to=settings.AUTH_USER_MODEL),
        ),
    ]
