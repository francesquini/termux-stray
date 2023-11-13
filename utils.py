import time
import datetime

exec(open('config.py').read())

def yieldF():
    #Python being python, doesn't have proper support for concurrent programing
    #So we fake a yield with a short sleep ARGH!!
    time.sleep(0.1)

def log(text):
    if LOGGING_ENABLED:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] {text}")
