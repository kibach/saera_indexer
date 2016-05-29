import time
from models import service_models
from saera_utils import config
from multiprocessing import Process, Queue, Lock, Event
from multiprocessing.dummy import dict as mpdict
from concurrency import worker


def load_queue(q):
    for item in service_models.Queue.select():
        q.put((item.url, item.depth, item.parent))
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
    stem_lock = Lock()
    work_allowance = Event()
    workers = []
    load_queue(queue)
    settings = load_settings(mpdict())
    for _ in xrange(config.BASIC_CONFIG['process_count']):
        p = worker.CrawlerIndexer(queue, stem_lock, work_allowance, settings)
        p.start()
        workers.append(p)

    work_allowance.set()
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

            elif task.type == "terminate":
                work_allowance.clear()
                time.sleep(5)
                for p in workers:
                    p.terminate()
                save_queue(queue)
                return

            else:
                task.delete_instance()

        time.sleep(float(settings['indexer_refresh_time']))
