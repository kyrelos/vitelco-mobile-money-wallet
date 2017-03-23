# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-22 23:14
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('bill_management', '0002_bill_bill_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='bill_reference',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='bill',
            name='due_date',
            field=models.DateTimeField(),
        ),
    ]
