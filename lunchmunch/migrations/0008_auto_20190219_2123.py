# Generated by Django 2.1.5 on 2019-02-20 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunchmunch', '0007_auto_20190219_0238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='code',
            field=models.CharField(default='A5F84F', editable=False, max_length=6),
        ),
    ]
