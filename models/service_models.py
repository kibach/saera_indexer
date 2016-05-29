from peewee import *
from saera_utils import config

db = MySQLDatabase(config.get_mysql_url())


class Setting(Model):
    name = CharField()
    value = CharField()


class Queue(Model):
    url = CharField()
    depth = IntegerField()
    parent = IntegerField()


class IndexerTask(Model):
    created_at = DateTimeField()
    type = CharField()
    parameters = TextField()
    completed = BooleanField()
