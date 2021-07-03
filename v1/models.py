from django.db import models


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    profile = models.CharField(max_length=500, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    token = models.CharField(max_length=500, blank=True, null=True)
    budget = models.BigIntegerField(blank=True, null=True)
    date = models.BigIntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(db_column='userId', max_length=50)  # Field name made lowercase.
    code = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    date = models.BigIntegerField(blank=True, null=True)
    payment = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction'


class Exclude(models.Model):
    exclude = models.BooleanField(default=True)


class Ask(models.Model):
    user_id = models.CharField(db_column='userId', max_length=50, blank=False, null=False)
    message = models.CharField(max_length=500, blank=True, null=True)
    version = models.CharField(max_length=100, blank=True, null=True)
    device = models.CharField(max_length=20, blank=True, null=True)
    os = models.IntegerField(blank=True, null=True)
    date = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ask'


class Notice(models.Model):
    subject = models.CharField(max_length=50, blank=False, null=False)
    content = models.CharField(max_length=500, blank=False, null=False)
    date = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notice'


class Reply(models.Model):
    message = models.CharField(max_length=500, blank=False, null=False)
    date = models.BigIntegerField(blank=True, null=False)
    ask_id = models.IntegerField(db_column='askId', blank=True, null=False)

    class Meta:
        managed = False
        db_table = 'reply'
