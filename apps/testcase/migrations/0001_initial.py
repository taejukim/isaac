# Generated by Django 3.1.2 on 2020-11-09 03:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Function',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('function_id', models.CharField(max_length=30)),
                ('function_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Service',
                'db_table': 'testcase_fuction',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Region',
                'db_table': 'testcase_region',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_id', models.CharField(max_length=30)),
                ('service_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Service',
                'db_table': 'testcase_service',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Testcase_history',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('testcase_id', models.CharField(max_length=100, unique=True)),
                ('summary', models.CharField(max_length=255)),
                ('precondition', models.TextField()),
                ('priority', models.CharField(max_length=5)),
                ('is_auto', models.BooleanField(default=False)),
                ('is_regression', models.BooleanField(default=False)),
                ('autor', models.CharField(max_length=50)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('version', models.IntegerField()),
                ('function', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testcase.function')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testcase.region')),
            ],
            options={
                'verbose_name': 'Testcase History',
                'db_table': 'testcase_testcase_history',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Testcase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('testcase_id', models.CharField(max_length=100, unique=True)),
                ('summary', models.CharField(max_length=255)),
                ('precondition', models.TextField()),
                ('priority', models.CharField(max_length=5)),
                ('is_auto', models.BooleanField(default=False)),
                ('is_regression', models.BooleanField(default=False)),
                ('autor', models.CharField(max_length=50)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('version', models.IntegerField()),
                ('function', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testcase.function')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testcase.region')),
            ],
            options={
                'verbose_name': 'Testcase',
                'db_table': 'testcase_testcase',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Procedure_history',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('procedure_id', models.IntegerField()),
                ('procedure', models.TextField()),
                ('expect_result', models.TextField()),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testcase.testcase_history', to_field='testcase_id')),
            ],
            options={
                'verbose_name': 'Procedure History',
                'db_table': 'testcase_procedure_history',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Procedure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('procedure_id', models.IntegerField()),
                ('procedure', models.TextField()),
                ('expect_result', models.TextField()),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testcase.testcase', to_field='testcase_id')),
            ],
            options={
                'verbose_name': 'Procedure',
                'db_table': 'testcase_procedure',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='function',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testcase.service'),
        ),
    ]
