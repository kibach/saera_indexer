from peewee import *
from saera_utils import config

db = MySQLDatabase(config.BASIC_CONFIG['mysql_db'], host=config.BASIC_CONFIG['mysql_host'], \
                   user=config.BASIC_CONFIG['mysql_user'], passwd=config.BASIC_CONFIG['mysql_pass'])


class Document(Model):
    url = CharField(index=True)
    domain = CharField(index=True)
    title = CharField()
    language = CharField()
    encoding = CharField()
    contents = TextField()
    plaintext = TextField()
    indexed_at = DateTimeField()

    class Meta:
        db_table = 'searchres_document'
        database = db


class Stem(Model):
    stem = CharField(unique=True)
    idf = FloatField()

    class Meta:
        db_table = 'searchres_stem'
        database = db


class DocumentMap(Model):
    A = IntegerField(index=True)
    B = IntegerField(index=True)

    class Meta:
        db_table = 'searchres_documentmap'
        database = db


class DocumentStemMap(Model):
    doc = ForeignKeyField(Document, index=True)
    stem = ForeignKeyField(Stem, index=True)
    count = IntegerField()
    type = IntegerField()
    rank_component = FloatField()

    class Meta:
        db_table = 'searchres_documentstemmap'
        database = db
