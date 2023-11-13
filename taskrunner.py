from queue import PriorityQueue
import threading
import time
from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class Task:
    when: int
    run: Any=field(compare=False)

class TaskRunner:
    def __init__(self):
        self.running = False
        self.queue = PriorityQueue()
        self.queue_cv = threading.Condition()

    def _consumer(self):
        while self.running:
            with self.queue_cv:
                if self.queue.empty():
                    self.queue_cv.wait()
                else: #Must be in an else branch to escape spurious wakes
                    task = self.queue.get()
                    due_in = task.when - time.time()
                    if due_in <= 0:
                        task.run()
                        self.queue.task_done()
                    else:
                        self.queue.put(task)
                        self.queue_cv.wait(due_in)

    def start(self):
        if not self.running:
            self.running = True
            thread = threading.Thread(target=self._consumer)
            thread.start()

    def stop(self):
        if self.running:
            with self.queue_cv:
                self.running = False
                self.queue_cv.notify()

    def enqueue(self, secs, run):
        when = secs + time.time()
        task = Task(when, run)
        with self.queue_cv:
            self.queue.put(task)
            self.queue_cv.notify()