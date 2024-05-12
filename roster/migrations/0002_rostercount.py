# Generated by Django 4.2.6 on 2023-11-30 05:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('roster', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RosterCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_At', models.DateTimeField(auto_now_add=True)),
                ('updated_At', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateField()),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_date', models.DateField()),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('hour_00', models.IntegerField(blank=True, null=True)),
                ('hour_01', models.IntegerField(blank=True, null=True)),
                ('hour_02', models.IntegerField(blank=True, null=True)),
                ('hour_03', models.IntegerField(blank=True, null=True)),
                ('hour_04', models.IntegerField(blank=True, null=True)),
                ('hour_05', models.IntegerField(blank=True, null=True)),
                ('hour_06', models.IntegerField(blank=True, null=True)),
                ('hour_07', models.IntegerField(blank=True, null=True)),
                ('hour_08', models.IntegerField(blank=True, null=True)),
                ('hour_09', models.IntegerField(blank=True, null=True)),
                ('hour_10', models.IntegerField(blank=True, null=True)),
                ('hour_11', models.IntegerField(blank=True, null=True)),
                ('hour_12', models.IntegerField(blank=True, null=True)),
                ('hour_13', models.IntegerField(blank=True, null=True)),
                ('hour_14', models.IntegerField(blank=True, null=True)),
                ('hour_15', models.IntegerField(blank=True, null=True)),
                ('hour_16', models.IntegerField(blank=True, null=True)),
                ('hour_17', models.IntegerField(blank=True, null=True)),
                ('hour_18', models.IntegerField(blank=True, null=True)),
                ('hour_19', models.IntegerField(blank=True, null=True)),
                ('hour_20', models.IntegerField(blank=True, null=True)),
                ('hour_21', models.IntegerField(blank=True, null=True)),
                ('hour_22', models.IntegerField(blank=True, null=True)),
                ('hour_23', models.IntegerField(blank=True, null=True)),
                ('count', models.IntegerField(default=0)),
                ('lob', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='roster_count_lob', to='accounts.lob')),
                ('process', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='roster_count_process', to='accounts.process')),
                ('site', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='roster_count_site', to='accounts.site')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
