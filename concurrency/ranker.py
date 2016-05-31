from models import index_models
from multiprocessing import Process
from peewee import *
from math import log


class Ranker(Process):

    def __init__(self, settings, ranking_event):
        Process.__init__(self)
        self.settings = settings
        self.event = ranking_event
        return

    def run(self):
        boost_factors = {
            '1': self.settings['field_1_boost'],
            '2': self.settings['field_2_boost'],
        }
        avg_length = {
            '1': index_models.Document.select(fn.Avg(fn.Length(index_models.Document.plaintext))),
            '2': index_models.Document.select(fn.Avg(fn.Length(index_models.Document.title))),
        }
        bm25_const = {
            'b': float(self.settings['bm25_b']),
            'k1': float(self.settings['bm25_k1']),
        }
        doc_cnt = index_models.DocumentStemMap.select().count()

        for relation in index_models.DocumentStemMap.select():
            if relation.type == 1:
                f_len = len(relation.doc.plaintext)
            else:
                f_len = len(relation.doc.title)

            rt = str(relation.type)
            w = relation.count * boost_factors[rt] / \
                ((1 - bm25_const['b']) + bm25_const['b'] * (f_len / avg_length[rt]))

            relation.rank_component = w
            relation.save()

            df = index_models.DocumentStemMap.select(index_models.DocumentStemMap.stem == relation.stem).count()
            z = (doc_cnt - df + 0.5) / (df + 0.5)
            if z > 0:
                relation.stem.idf = log(z)
                relation.stem.save()

        self.event.clear()
        return
