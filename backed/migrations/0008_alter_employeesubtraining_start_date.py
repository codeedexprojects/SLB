# Generated by Django 3.2.10 on 2024-05-21 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backed', '0007_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeesubtraining',
            name='start_date',
            field=models.DateField(),
        ),
    ]
