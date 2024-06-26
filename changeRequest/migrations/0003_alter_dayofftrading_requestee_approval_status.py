# Generated by Django 4.2.6 on 2023-11-08 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('changeRequest', '0002_alter_dayofftrading_supervisor_approval_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dayofftrading',
            name='requestee_approval_status',
            field=models.CharField(blank=True, choices=[('', '----'), ('approved', 'Approved'), ('rejected', 'Rejected')], default=None, max_length=50, null=True),
        ),
    ]
