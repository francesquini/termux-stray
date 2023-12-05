import pystray
from PIL import Image
import json
import subprocess

exec(open('config.py').read())

class BatteryStatus:
    def __init__(self):
        self.state = {}

    def updateState(self):
        vout = subprocess.run([BATTERY_CMD], stdout=subprocess.PIPE).stdout
        self.state = json.loads(vout.decode('utf-8'))

    def handleCommand(self, command):
        #There are no commands associated with battery
        return None

    def getPercentage(self):
        return self.state.get("percentage", 0)

    def isCharging(self):
        return self.state.get("status", "unknown") == "CHARGING"

    def isPlugged(self):
        return self.state.get("plugged", "unknown") == "PLUGGED_USB"

    def getStateDict(self):
        return self.state

class BatteryStray:
    def __init__(self, batStatus):
        self.batStatus = batStatus
        self.icon = None
        self.battery_icons = {}
        self.plugged_icon = None

    def start(self):
        self.icon = pystray.Icon(
                "Termux Battery Status",
                title="Battery",
                menu=self._generateMenu()
            )
        self.icon.icon = self._batteryIcon()
        if BATTERY_DEDICATED_PLUGGED_IN_ICON:
            self.plugged_icon = pystray.Icon(
                "Termux Energy Source Status",
                title="Plugged")
            self.plugged_icon.icon = Image.open(BATTERY_ICON_ON_AC_ADAPTER)
            self.plugged_icon.run_detached()
        self.icon.run()

    def updateState(self):
        self._iconUpdate()
        if self.plugged_icon:
            self.plugged_icon.visible = self.batStatus.isPlugged()

    def handleCommand(self, command):
        #There are no commands associated with battery
        return None

    def _getBatteryAproxPercentage(self):
        return (self.batStatus.getPercentage() // 10) * 10

    def _batteryIcon(self):
        ifn = BATTERY_ICON_FILE_PREFIX + \
              f"{self._getBatteryAproxPercentage():03}" + \
              (BATTERY_ICON_CHARGING_SUFFIX if self.batStatus.isCharging() else "") + \
              BATTERY_ICON_FILE_EXTENSION
        if ifn not in self.battery_icons:
            png = Image.open(ifn)
            self.battery_icons[ifn] = png
        else:
            png = self.battery_icons[ifn]
        return png

    def _iconUpdate(self):
        self.icon.icon = self._batteryIcon()
        self.icon.menu = self._generateMenu()
        self.icon.update_menu()

    def _generateMenu(self):
        dict = self.batStatus.getStateDict()
        menu = pystray.Menu(lambda: list((
                          pystray.MenuItem(
                              f"{i}: {dict[i]}",
                              None
                          )
                          for i in list(dict))) + \
                          [pystray.Menu.SEPARATOR,
                           pystray.MenuItem(
                             "Quit",
                             lambda: exit(0)
                           )])
        return menu
