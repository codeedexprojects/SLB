# Generated by Django 3.2.10 on 2024-05-19 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backed', '0003_alter_subtraining_validity_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='on_duty',
            field=models.BooleanField(default=False),
        ),
    ]
