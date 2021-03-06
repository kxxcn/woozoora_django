# Generated by Django 3.1.5 on 2021-01-18 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10)),
                ('email', models.CharField(max_length=50)),
                ('profile', models.CharField(max_length=500)),
                ('code', models.CharField(max_length=20)),
                ('token', models.CharField(max_length=500)),
                ('budget', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'user',
                'managed': False,
            },
        ),
    ]
