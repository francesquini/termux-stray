import os
import errno
import threading


class PipeControl:
    def __init__(self, fpath, callback):
        self.fpath = fpath
        self.callback = callback

    def start(self):
        th = threading.Thread(target=self._loop)
        th.start()

    def _loop(self):
        try:
            os.mkfifo(self.fpath)
        except OSError as oe:
            if oe.errno != errno.EEXIST:
                raise
            while True:
                with open(self.fpath) as fifo:
                    while True:
                        data = fifo.read()
                        if len(data) == 0:
                            break
                        [self.callback (cmd) for cmd in data.splitlines()]
