# Generated by Django 4.2.6 on 2023-12-29 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_attendance_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('user', 'time')},
        ),
    ]
