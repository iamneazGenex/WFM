# Generated by Django 4.2.6 on 2023-12-04 06:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('roster', '0005_alter_rostercount_hour_00_alter_rostercount_hour_01_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rostercount',
            name='workRole',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='roster_count_workRole', to='accounts.workrole'),
        ),
    ]
