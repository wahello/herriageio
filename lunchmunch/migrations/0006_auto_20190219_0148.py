# Generated by Django 2.1.5 on 2019-02-19 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunchmunch', '0005_auto_20190218_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='code',
            field=models.CharField(default='53547A', editable=False, max_length=6),
        ),
    ]
