import time
import datetime
import threading
import croniter


class CronService:
    def __init__(self):
        self.cron_jobs = {}
        self.thread = None

    def add_cron_job(self, name, cron_expression, task):
        self.cron_jobs[name] = (cron_expression, task)

    def remove_cron_job(self, name):
        del self.cron_jobs[name]

    def get_cron_jobs(self):
        return list(self.cron_jobs.keys())

    def start(self):
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

    def start_job(self, name):
        if name in self.cron_jobs:
            cron_expression, task = self.cron_jobs[name]
            self.cron_jobs[name] = (cron_expression, task)

    def _run(self):
        while True:
            current_time = time.time()
            for name, (cron_expression, task) in self.cron_jobs.items():
                next_time = croniter.croniter(cron_expression, current_time).get_next()
                if next_time <= current_time:
                    threading.Thread(target=task).start()
            time.sleep(1)