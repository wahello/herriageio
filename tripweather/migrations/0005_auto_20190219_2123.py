# Generated by Django 2.1.5 on 2019-02-20 03:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tripweather', '0004_auto_20190219_0148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='date',
            field=models.DateTimeField(default=datetime.date(2019, 2, 20)),
        ),
    ]