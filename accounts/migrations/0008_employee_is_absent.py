# Generated by Django 4.2.6 on 2024-03-11 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_employee_avaya_id_employee_doj_employee_vdi'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_absent',
            field=models.IntegerField(blank=True, default=0, editable=False, null=True),
        ),
    ]
