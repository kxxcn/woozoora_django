# Generated by Django 3.1.5 on 2021-03-22 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('v1', '0003_exclude'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(blank=True, max_length=500, null=True)),
                ('version', models.CharField(blank=True, max_length=100, null=True)),
                ('device', models.CharField(blank=True, max_length=20, null=True)),
                ('os', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ask',
                'managed': False,
            },
        ),
    ]
