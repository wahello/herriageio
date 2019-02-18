# Generated by Django 2.1.5 on 2019-02-15 05:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('at', models.DateTimeField()),
                ('status', models.CharField(blank=True, choices=[('upcoming', 'upcoming'), ('starting', 'starting'), ('in_progress', 'in_progress'), ('vetoing', 'vetoing'), ('completing', 'completing'), ('completed', 'completed'), ('archived', 'archived')], default='upcoming', max_length=48, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Event',
                'verbose_name_plural': 'Events',
                'ordering': ['at'],
            },
        ),
        migrations.CreateModel(
            name='FavoriteRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Favorite Request',
                'verbose_name_plural': 'Favorite Requests',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=248, null=True)),
                ('has_custom_name', models.BooleanField(default=False)),
                ('code', models.CharField(default='115E05', editable=False, max_length=6)),
                ('checked_code', models.BooleanField(default=False)),
                ('event_starting_seconds', models.PositiveIntegerField(default=30)),
                ('in_progress_seconds', models.PositiveIntegerField(default=120)),
                ('vetoing_seconds_per_user', models.PositiveIntegerField(default=15)),
                ('completing_seconds', models.PositiveIntegerField(default=30)),
                ('leader', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leader', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Group',
                'verbose_name_plural': 'Groups',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='GroupEventHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.IntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], unique=True)),
                ('from_hour', models.TimeField()),
                ('to_hour', models.TimeField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lunchmunch.Group')),
            ],
        ),
        migrations.CreateModel(
            name='GroupInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('active', 'active'), ('declined', 'declined'), ('accepted', 'accepted'), ('archived', 'archived')], max_length=48, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lunchmunch.Group')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_invite_receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_invite_sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Group Invite',
                'verbose_name_plural': 'Group Invite',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='LunchMunchProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zipcode', models.CharField(blank=True, max_length=5, null=True)),
                ('favorite_users', models.ManyToManyField(related_name='favorite_users', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'LunchMunchProfile',
                'verbose_name_plural': 'LunchMunchProfiles',
            },
        ),
        migrations.CreateModel(
            name='PreferenceAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='PreferenceProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='PreferenceQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lunchmunch.Group'),
        ),
    ]