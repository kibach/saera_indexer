from peewee import *
from saera_utils import config

db = MySQLDatabase(config.get_mysql_url())


class Document(Model):
    url = CharField(index=True)
    domain = CharField(index=True)
    title = CharField()
    language = CharField()
    encoding = CharField()
    contents = TextField()
    plaintext = TextField()
    indexed_at = DateTimeField()


class Stem(Model):
    stem = CharField(unique=True)


class DocumentMap(Model):
    A = IntegerField(index=True)
    B = IntegerField(index=True)


class DocumentStemMap(Model):
    doc = ForeignKeyField(Document, index=True)
    stem = ForeignKeyField(Stem, index=True)
    count = IntegerField()
    type = IntegerField()
