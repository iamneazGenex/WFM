# Generated by Django 4.2.6 on 2024-05-19 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0032_alter_roster_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roster',
            name='shiftLegend',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rosterShiftLegend', to='roster.shiftlegend'),
        ),
    ]