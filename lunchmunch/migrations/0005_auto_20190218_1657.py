# Generated by Django 2.1.5 on 2019-02-18 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunchmunch', '0004_auto_20190218_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='code',
            field=models.CharField(default='01CEE6', editable=False, max_length=6),
        ),
    ]
