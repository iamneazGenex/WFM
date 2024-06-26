# Generated by Django 4.2.6 on 2024-05-19 09:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_alter_employee_pick_drop_location'),
        ('roster', '0031_alter_roster_shiftlegend'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roster',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rosterEmployee', to='accounts.employee'),
        ),
    ]
