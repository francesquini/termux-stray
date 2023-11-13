#!/data/data/com.termux/files/usr/bin/env python
import os
import threading

os.chdir(os.path.dirname(os.path.realpath(__file__)))
exec(open('config.py').read())

from taskrunner import TaskRunner
from pipecontrol import PipeControl
from volumestray import VolumeStray
from batterystray import BatteryStray, BatteryStatus
from wifistray import WifiStray
from utils import log, yieldF

taskrunner = None
pipecontrol = None
tasks = []
tasks_threads = []
battery_status = None

def currentUpdateInterval():
    if not battery_status:
        # so that we can update as soon as possible and we can update
        # our status accordingly
        return PLUGGED_UPDATE_INTERVAL
    if BATTERY_THROTTLE_ENABLE and not battery_status.isPlugged():
        log("On battery. Throttling enabled.")
        return UNPLUGGED_UPDATE_INTERVAL
    else:
        return PLUGGED_UPDATE_INTERVAL

def updateStates():
    log("Updating states")
    for st in tasks:
        st.updateState()
    updIntvl = currentUpdateInterval()
    log(f"Update complete. Next update in {updIntvl} seconds.")
    taskrunner.enqueue(updIntvl, updateStates)

def controlCallback(command):
    for st in tasks:
        action = st.handleCommand(command)
        if action:
            #-1 guarantees that it will be run as soon as possible
            taskrunner.enqueue(-1, action)
            return
    print(f"No handlers for <{command}> found.")

def addTask(task):
    tasks.append(task)
    tasks_threads.append(None)

def addStray(stray):
    tasks.append(stray)
    th = threading.Thread(target=stray.start)
    tasks_threads.append(th)
    th.start()
    #this yield is necessary to guarantee icon ordering. BUT...  since
    #the yield impl. is a kludge, you might need to increase the delay
    #inside the utils module to make it work
    yieldF()

if __name__ == "__main__":
    taskrunner = TaskRunner()
    taskrunner.start()
    print("Task runner started.")

    pipecontrol = PipeControl(
        f"{os.getenv('TMPDIR')}/{CONTROL_PIPE_PATH}",
        controlCallback)
    pipecontrol.start()
    print("Pipe interface started.")


    battery_status = BatteryStatus()
    addTask(battery_status)

    if BATTERY_SYSTRAY_ENABLE:
        addStray(BatteryStray(battery_status))

    if WIFI_SYSTRAY_ENABLE:
        addStray(WifiStray())

    if VOLUME_SYSTRAY_ENABLE:
        addStray(VolumeStray())

    # Performs first update immediatelly
    taskrunner.enqueue(0, updateStates)

    print("Initialization complete.")
