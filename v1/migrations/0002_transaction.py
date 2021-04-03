# Generated by Django 3.1.5 on 2021-01-21 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('v1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(db_column='userId', max_length=50)),
                ('code', models.CharField(blank=True, max_length=20, null=True)),
                ('category', models.CharField(blank=True, max_length=20, null=True)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('price', models.IntegerField(blank=True, null=True)),
                ('date', models.BigIntegerField(blank=True, null=True)),
                ('payment', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'transaction',
                'managed': False,
            },
        ),
    ]
