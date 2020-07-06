from datetime import datetime

from peewee import *
from playhouse.sqlite_ext import JSONField

database = SqliteDatabase(None)


class BaseModel(Model):
    id = PrimaryKeyField()
    created_at = TimestampField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    updated_at = TimestampField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        database = database


class User(BaseModel):
    chat_id = CharField(max_length=128, unique=True)
    first_name = CharField(max_length=128, null=True)
    last_name = CharField(max_length=128, null=True)
    username = CharField(max_length=128, null=True)
    language_code = CharField(max_length=20, null=True)
    is_bot = BooleanField(default=False)

    digikala_email = CharField(null=True)
    digikala_password = CharField(null=True)

    def __str__(self):
        return "{} {} (@{})".format(self.first_name, self.last_name, self.username)


class Message(BaseModel):
    chat_id = CharField(max_length=128)
    username = CharField(max_length=128, null=True)
    text = CharField(max_length=128, null=True)
    date = DateTimeField(default=datetime.now)
    details = JSONField(default=dict, null=True)


class CheckList(BaseModel):
    user = ForeignKeyField(User, related_name='check_list', lazy_load=False)
    url = CharField()
    maximum_price = IntegerField(default=0)
    check_until = DateTimeField(null=True)
    is_active = BooleanField(default=True)
