# Generated by Django 4.0.4 on 2022-05-29 23:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gradingsystem', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='semester',
            unique_together={('year', 'semester')},
        ),
    ]
