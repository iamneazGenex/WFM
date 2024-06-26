# Generated by Django 4.2.6 on 2024-05-19 05:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_alter_employee_pick_drop_location'),
        ('roster', '0029_roster_gender_roster_lob_roster_pick_drop_location_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roster',
            name='supervisor_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rosterSupervisor1', to='accounts.employee'),
        ),
        migrations.AlterField(
            model_name='roster',
            name='supervisor_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rosterSupervisor2', to='accounts.employee'),
        ),
    ]
