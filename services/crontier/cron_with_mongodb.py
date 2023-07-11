import datetime
import threading
import time
import croniter
import pymongo


class CronService:
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.cron_jobs = {}
        self.thread = None

    def add_cron_job(self, name, cron_expression, task):
        self.cron_jobs[name] = (cron_expression, task)
        self._save_job_to_db(name, cron_expression, task)

    def remove_cron_job(self, name):
        del self.cron_jobs[name]
        self._remove_job_from_db(name)

    def get_cron_jobs(self):
        return list(self.cron_jobs.keys())

    def start(self):
        self._load_jobs_from_db()
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        if self.thread is not None:
            self.thread.cancel()
            self.thread = None

    def restart(self):
        self.stop()
        self.start()

    def stop_all_jobs(self):
        for job in self.cron_jobs:
            self.stop_job(job)

    def start_all_jobs(self):
        for job in self.cron_jobs:
            self.start_job(job)

    def stop_job(self, name):
        if name in self.cron_jobs:
            del self.cron_jobs[name]
            self._remove_job_from_db(name)

    def start_job(self, name):
        if name in self.cron_jobs:
            cron_expression, task = self.cron_jobs[name]
            self.cron_jobs[name] = (cron_expression, task)
            self._save_job_to_db(name, cron_expression, task)

    def _run(self):
        while True:
            current_time = time.time()
            for name, (cron_expression, task) in self.cron_jobs.items():
                next_time = croniter.croniter(cron_expression, current_time).get_next()
                if next_time <= current_time:
                    threading.Thread(target=task).start()
            time.sleep(1)

    def _save_job_to_db(self, name, cron_expression, task):
        with pymongo.MongoClient(self.mongo_uri) as client:
            db = client[self.mongo_db]
            collection = db[self.mongo_collection]
            collection.update_one(
                {"name": name},
                {"$set": {"cron_expression": cron_expression, "task": task.__name__}},
                upsert=True,
            )

    def _remove_job_from_db(self, name):
        with pymongo.MongoClient(self.mongo_uri) as client:
            db = client[self.mongo_db]
            collection = db[self.mongo_collection]
            collection.delete_one({"name": name})

    def _load_jobs_from_db(self):
        with pymongo.MongoClient(self.mongo_uri) as client:
            db = client[self.mongo_db]
            collection = db[self.mongo_collection]
            for job in collection.find():
                name = job["name"]
                cron_expression = job["cron_expression"]
                task_name = job["task"]
                task = globals()[task_name]
                self.cron_jobs[name] = (cron_expression, task)