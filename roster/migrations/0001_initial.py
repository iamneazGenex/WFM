# Generated by Django 4.2.6 on 2023-10-31 05:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_At', models.DateTimeField(auto_now_add=True)),
                ('updated_At', models.DateTimeField(auto_now=True)),
                ('consecutive_working_days', models.IntegerField(default=0)),
                ('maximum_regular_shift_duration', models.IntegerField(default=0)),
                ('minimum_regular_shift_duration', models.IntegerField(default=0)),
                ('gap_between_shift_end_to_the_next_shift_start_time', models.IntegerField(default=0)),
                ('female_shift_start_time', models.TimeField()),
                ('female_shift_end_time', models.TimeField()),
                ('prohibited_time_for_end_of_a_shift_start_time', models.TimeField()),
                ('prohibited_time_for_end_of_a_shift_end_time', models.TimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Roster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_At', models.DateTimeField(auto_now_add=True)),
                ('updated_At', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateField()),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_date', models.DateField()),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rosterEmployee', to='accounts.employee')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
