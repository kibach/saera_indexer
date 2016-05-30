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

    class Meta:
        db_table = 'searchres_document'


class Stem(Model):
    stem = CharField(unique=True)

    class Meta:
        db_table = 'searchres_stem'


class DocumentMap(Model):
    A = IntegerField(index=True)
    B = IntegerField(index=True)

    class Meta:
        db_table = 'searchres_documentmap'


class DocumentStemMap(Model):
    doc = ForeignKeyField(Document, index=True)
    stem = ForeignKeyField(Stem, index=True)
    count = IntegerField()
    type = IntegerField()

    class Meta:
        db_table = 'searchres_documentstemmap'
