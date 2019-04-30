# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0002_testinfo_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChineseScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10)),
                ('gender', models.CharField(max_length=5)),
                ('age', models.IntegerField(default=0)),
                ('chinese_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='MathScores',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10)),
                ('gender', models.CharField(max_length=5)),
                ('age', models.IntegerField(default=0)),
                ('math_score', models.IntegerField(default=0)),
                ('english_score', models.IntegerField(default=0)),
            ],
        ),
    ]
