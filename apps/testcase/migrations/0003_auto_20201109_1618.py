# Generated by Django 3.1.2 on 2020-11-09 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testcase', '0002_auto_20201109_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testcase',
            name='testcase_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
