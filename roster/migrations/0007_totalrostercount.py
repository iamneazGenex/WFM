# Generated by Django 4.2.6 on 2023-12-05 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('roster', '0006_rostercount_workrole'),
    ]

    operations = [
        migrations.CreateModel(
            name='TotalRosterCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_At', models.DateTimeField(auto_now_add=True)),
                ('updated_At', models.DateTimeField(auto_now=True)),
                ('total', models.IntegerField(default=0)),
                ('lob', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='total_roster_count_lob', to='accounts.lob')),
                ('process', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='total_roster_count_process', to='accounts.process')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
