# Generated by Django 4.2.6 on 2023-12-25 13:39

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=100)),
                ('loan_amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_paid', models.DateField()),
                ('commission', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RoutePlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('agent', models.CharField(max_length=100)),
                ('institution', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Commission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commission_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('agent', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_fullname', models.CharField(max_length=255)),
                ('id_number', models.CharField(max_length=8, unique=True, validators=[django.core.validators.RegexValidator(message='ID number must be 7 to 8 digits long.', regex='^[0-9]{7,8}$')])),
                ('phone_number', models.CharField(max_length=12, validators=[django.core.validators.RegexValidator(message='Phone number must be 10 to 12 digits long.', regex='^[0-9]{10,12}$')])),
                ('ministry', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('prospects', 'Prospects'), ('lead', 'Lead'), ('conversion', 'Conversion')], max_length=20)),
                ('pf_number', models.CharField(blank=True, max_length=255, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('pf_number_conversion', models.CharField(blank=True, max_length=255, null=True)),
                ('password', models.CharField(blank=True, max_length=255, null=True)),
                ('amount_applied', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('date_field', models.DateField(blank=True, null=True)),
                ('comment_conversion', models.TextField(blank=True, null=True)),
                ('type_loan_qualify', models.CharField(blank=True, choices=[('refinance', 'Refinance'), ('topup', 'Top-Up'), ('buyoff', 'Buy-Off')], max_length=20, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('location', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'date')},
            },
        ),
    ]