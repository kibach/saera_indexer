from peewee import *
from saera_utils import config

db = MySQLDatabase(config.get_mysql_url())


class Setting(Model):
    name = CharField()
    value = CharField()

    class Meta:
        db_table = 'searchres_setting'


class Queue(Model):
    url = CharField()
    depth = IntegerField()
    parent = IntegerField()

    class Meta:
        db_table = 'searchres_queue'


class IndexerTask(Model):
    created_at = DateTimeField()
    type = CharField()
    parameters = TextField()
    completed = BooleanField()

    class Meta:
        db_table = 'searchres_indexertask'
