from peewee import *
from saera_utils import config

db = MySQLDatabase(config.BASIC_CONFIG['mysql_db'], host=config.BASIC_CONFIG['mysql_host'], \
                   user=config.BASIC_CONFIG['mysql_user'], passwd=config.BASIC_CONFIG['mysql_pass'])


class Setting(Model):
    name = CharField()
    value = CharField()

    class Meta:
        db_table = 'searchres_setting'
        database = db


class Queue(Model):
    url = CharField()
    depth = IntegerField()
    parent = IntegerField()

    class Meta:
        db_table = 'searchres_queue'
        database = db


class IndexerTask(Model):
    created_at = DateTimeField()
    type = CharField()
    parameters = TextField()
    completed = BooleanField()

    class Meta:
        db_table = 'searchres_indexertask'
        database = db
