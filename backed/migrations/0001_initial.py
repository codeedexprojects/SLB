# Generated by Django 3.2.10 on 2024-05-19 08:58

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=100)),
                ('mobile_number', models.CharField(max_length=15)),
                ('designation', models.CharField(max_length=100)),
                ('gate_pass_no', models.CharField(max_length=50)),
                ('rig_or_rigless', models.CharField(choices=[('Rig', 'Rig'), ('Rigless', 'Rigless')], default='choice', max_length=50)),
                ('profile_photo', models.ImageField(blank=True, null=True, upload_to='profile_photos/')),
                ('is_accepted', models.BooleanField(default=False)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backed.company')),
            ],
        ),
        migrations.CreateModel(
            name='MainTraining',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SubTraining',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('validity_period', models.DurationField(blank=True, choices=[(datetime.timedelta(days=182), '6 months'), (datetime.timedelta(days=365), '1 year'), (datetime.timedelta(days=730), '2 years'), (datetime.timedelta(days=1095), '3 years'), (None, 'Permanent')], null=True)),
                ('main_training', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_trainings', to='backed.maintraining')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeSubTraining',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(auto_now_add=True)),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('warning', models.BooleanField(default=False)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_trainings', to='backed.employee')),
                ('sub_training', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_sub_trainings', to='backed.subtraining')),
            ],
        ),
        migrations.AddField(
            model_name='employee',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backed.project'),
        ),
    ]
