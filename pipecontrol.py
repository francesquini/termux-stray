import os
import errno
import threading
from utils import log

class PipeControl:
    def __init__(self, fpath, callback):
        self.fpath = fpath
        self.callback = callback

    def start(self):
        th = threading.Thread(target=self._loop)
        th.start()

    def _loop(self):
        log("[CP] Creating pipe")
        try:
            os.mkfifo(self.fpath)
        except OSError as oe:
            if oe.errno != errno.EEXIST:
                raise
            while True:
                log("[CP] Opening pipe")
                with open(self.fpath) as fifo:
                    while True:
                        log("[CP] Waiting to read from pipe")
                        data = fifo.read()
                        if len(data) == 0:
                            log("[CP] Read 0 byte")
                            break
                        log ("[CP] Running callbaks")
                        [self.callback (cmd) for cmd in data.splitlines()]
