# Generated by Django 3.2.10 on 2024-05-21 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backed', '0006_alter_employee_gate_pass_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
