# Generated by Django 4.2.6 on 2023-12-28 17:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_notification'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='managementadmin',
            name='active',
        ),
        migrations.RemoveField(
            model_name='managementadmin',
            name='banned',
        ),
        migrations.RemoveField(
            model_name='managementadmin',
            name='experience',
        ),
        migrations.AddField(
            model_name='attendance',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='latitude',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='longitude',
            field=models.FloatField(),
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='date',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='location',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='timestamp',
        ),
    ]