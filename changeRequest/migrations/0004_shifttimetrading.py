# Generated by Django 4.2.6 on 2023-11-16 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0001_initial'),
        ('accounts', '0001_initial'),
        ('changeRequest', '0003_alter_dayofftrading_requestee_approval_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShiftTimeTrading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_At', models.DateTimeField(auto_now_add=True)),
                ('updated_At', models.DateTimeField(auto_now=True)),
                ('requestor_start_time', models.TimeField()),
                ('requestor_end_time', models.TimeField()),
                ('requestee_start_time', models.TimeField()),
                ('requestee_end_time', models.TimeField()),
                ('requestee_approval_status', models.CharField(blank=True, choices=[('', '----'), ('approved', 'Approved'), ('rejected', 'Rejected')], default=None, max_length=50, null=True)),
                ('requestee_approval_status_datetime', models.DateTimeField(blank=True, null=True)),
                ('supervisor_approval_status', models.CharField(blank=True, choices=[('', '----'), ('approved', 'Approved'), ('rejected', 'Rejected')], default=None, max_length=50, null=True)),
                ('supervisor_approval_status_datetime', models.DateTimeField(blank=True, null=True)),
                ('trading_status', models.CharField(choices=[('', '----'), ('in process', 'In Process'), ('approved', 'Approved'), ('rejected', 'Rejected')], default=None, max_length=50)),
                ('requestee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_time_trading_requestee', to='accounts.employee')),
                ('requestee_swap_roster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requestee_shift_time_swap_roster', to='roster.roster')),
                ('requestor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_time_trading_requestor', to='accounts.employee')),
                ('requestor_swap_roster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requestor_shift_time_swap_roster', to='roster.roster')),
                ('supervisor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shift_time_trading_supervisor', to='accounts.supervisor')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
