# Generated by Django 4.2.6 on 2024-04-25 03:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_employee_is_absent'),
        ('reporting', '0013_remove_agenthourlyperformance_is_absent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agenthourlyperformance',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agentHourlyPerformance_employee', to='accounts.employee'),
        ),
    ]
