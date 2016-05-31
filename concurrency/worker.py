from models import index_models
from multiprocessing import Process
import time
import datetime
from parsers import webpage


class CrawlerIndexer(Process):

    def __init__(self, task_queue, url_lookup_lock, stem_lock, work_allowance, settings):
        Process.__init__(self)
        self.task_queue = task_queue
        self.url_lookup_lock = url_lookup_lock
        self.stem_lock = stem_lock
        self.work_allowed = work_allowance
        self.settings = settings
        return

    def run(self):
        while True:
            if self.work_allowed.is_set():
                url, depth, parent = self.task_queue.get()

                self.url_lookup_lock.acquire()

                try:
                    u = index_models.Document.get(index_models.Document.url == url)
                except:
                    u = None

                if u:
                    continue

                page = webpage.WebPage(url)
                success, e = page.request()
                if not success:
                    continue
                doc = index_models.Document()
                doc.url = url
                doc.domain = page.get_domain()
                doc.title = page.get_title()
                doc.language = page.get_language()
                doc.encoding = page.get_encoding()
                doc.plaintext = page.get_plaintext()
                doc.contents = page.get_contents()
                doc.indexed_at = datetime.datetime.now()
                doc.save()
                self.url_lookup_lock.release()

                body_stemmas = page.get_all_stemmas()
                for stem in body_stemmas:
                    self.stem_lock.acquire()

                    try:
                        s = index_models.Stem()
                        s.stem = stem
                        s.save()
                    except:
                        s = index_models.Stem.get(index_models.Stem.stem == stem)

                    self.stem_lock.release()

                    m = index_models.DocumentStemMap()
                    m.stem = s
                    m.doc = doc
                    m.count = body_stemmas[stem]
                    m.type = 1
                    m.save()

                title_stemmas = page.get_title_stemmas()
                for stem in title_stemmas:
                    self.stem_lock.acquire()

                    try:
                        s = index_models.Stem()
                        s.stem = stem
                        s.save()
                    except:
                        s = index_models.Stem.get(index_models.Stem.stem == stem)

                    self.stem_lock.release()

                    m = index_models.DocumentStemMap()
                    m.stem = s
                    m.doc = doc
                    m.count = title_stemmas[stem]
                    m.type = 2
                    m.save()

                if int(self.settings['max_depth']) == -1 or int(self.settings['max_depth']) > depth:
                    i = 0
                    for link in page.get_all_links():
                        try:
                            u = index_models.Document.get(index_models.Document.url == link)
                        except:
                            u = None
                        if u:
                            continue
                        self.task_queue.put((link, depth + 1, doc.id))
                        i += 1
                        if i == int(self.settings['max_width']):
                            break

                if parent > 0:
                    rel = index_models.DocumentMap()
                    rel.A = doc.id
                    rel.B = parent
                    rel.save()
                    rel = index_models.DocumentMap()
                    rel.B = doc.id
                    rel.A = parent
                    rel.save()

                time.sleep(float(self.settings['sleep_between_urls']))
            else:
                time.sleep(0.5)
