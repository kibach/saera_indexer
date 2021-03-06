import time
import atexit
from models import service_models
from saera_utils import config
from multiprocessing import Process, Queue, Lock, Event
from multiprocessing.dummy import dict as mpdict
from concurrency import worker
from concurrency import ranker


def load_queue(q):
    for item in service_models.Queue.select():
        q.put((item.url, item.depth, item.parent))
        item.delete_instance()
    return


def save_queue(q):
    while not q.empty():
        queue_item = q.get()
        queue_record = service_models.Queue()
        queue_record.url = queue_item[0]
        queue_record.depth = queue_item[1]
        queue_record.parent = queue_item[2]
        queue_record.save()
    return


def load_settings(stgs):
    for setting in service_models.Setting.select():
        stgs[setting.name] = setting.value
    return stgs


def father_thread():
    queue = Queue()
    url_lookup_lock = Lock()
    stem_lock = Lock()
    work_allowance = Event()
    ranking_event = Event()
    workers = []
    load_queue(queue)
    settings = load_settings(mpdict())
    atexit.register(lambda: save_queue(queue))

    for _ in xrange(config.BASIC_CONFIG['process_count']):
        p = worker.CrawlerIndexer(queue, url_lookup_lock, stem_lock, work_allowance, settings)
        p.start()
        workers.append(p)

    work_allowance.set()
    rank_process = None
    while True:
        tasks = service_models.IndexerTask.select().where(service_models.IndexerTask.completed == False)
        for task in tasks:
            if task.type == "pause":
                work_allowance.clear()
                task.completed = True
                task.save()

            elif task.type == "resume":
                work_allowance.set()
                task.completed = True
                task.save()

            elif task.type == "update_settings":
                settings = load_settings(settings)
                task.completed = True
                task.save()

            elif task.type == "reload_queue":
                load_queue(queue)
                task.completed = True
                task.save()

            elif task.type == "terminate":
                work_allowance.clear()
                if rank_process is not None and rank_process.is_alive():
                    rank_process.terminate()
                time.sleep(5)
                for p in workers:
                    p.terminate()
                save_queue(queue)
                task.completed = True
                task.save()
                return

            else:
                task.delete_instance()

        if not ranking_event.is_set():
            ranking_event.set()
            if rank_process is not None and rank_process.is_alive():
                rank_process.terminate()
            rank_process = ranker.Ranker(settings, ranking_event)
            rank_process.start()

        time.sleep(float(settings['indexer_refresh_time']))
