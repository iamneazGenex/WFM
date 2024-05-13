# Generated by Django 4.2.6 on 2024-05-13 20:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_customuser_system_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='lob',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employeeLOB', to='accounts.lob'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employeeSite', to='accounts.site'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='work_role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employeeWorkRole', to='accounts.workrole'),
        ),
    ]
