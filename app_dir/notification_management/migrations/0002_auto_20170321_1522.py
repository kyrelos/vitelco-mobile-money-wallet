# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-21 12:22
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('notification_management', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationDeviceMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('msisdn', models.CharField(blank=True, max_length=20, null=True)),
                ('token', models.CharField(blank=True, max_length=256, null=True)),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('team_name', models.CharField(blank=True, max_length=64, null=True)),
                ('user_type', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='notification',
            name='type',
        ),
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[(b'push', b'push'), (b'normal', b'normal')], default='normal', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notification',
            name='notid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='state',
            field=models.CharField(choices=[(b'pending', b'pending'), (b'in_progress', b'in_progress'), (b'success', b'success'), (b'failed', b'failed')], default=b'pending', max_length=20),
        ),
    ]
