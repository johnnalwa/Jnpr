# Generated by Django 4.2.6 on 2023-12-29 13:57

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_attendance_unique_together_attendance_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='date',
            field=models.DateField(default=accounts.models.get_current_date, null=True),
        ),
    ]
