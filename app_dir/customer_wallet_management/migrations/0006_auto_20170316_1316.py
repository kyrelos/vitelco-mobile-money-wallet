# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-16 10:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_wallet_management', '0005_auto_20170316_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerwallet',
            name='token',
            field=models.CharField(max_length=256, null=True, unique=True),
        ),
    ]
