import pystray
from PIL import Image
import json
import subprocess

exec(open('config.py').read())

class WifiStray:
    def __init__(self):
        self.state = {}
        self.icon = None
        self.icons = {}

    def start(self):
        self.icon = pystray.Icon(
                "Termux Wifi Status",
                title="Wifi",
                menu=self._generateMenu()
            )
        self.icon.icon = self._wifiIcon()
        self.icon.run()

    def updateState(self):
        vout = subprocess.run([WIFI_CMD], stdout=subprocess.PIPE).stdout
        self.state = json.loads(vout.decode('utf-8'))
        self._iconUpdate()

    def handleCommand(self, command):
        #There are no commands associated with wifi
        return None

    def _getSignalAproxStrength(self):
        rssi = self._getSignalStrength()
        if rssi >= WIFI_ICON_EXCELLENT_THOLD:
            return "excellent"
        elif rssi >= WIFI_ICON_GOOD_THOLD:
            return "good"
        elif rssi >= WIFI_ICON_OK_THOLD:
            return "ok"
        elif rssi >= WIFI_ICON_LOW_THOLD:
            return "low"
        else:
            return "none"

    def _getSignalStrength(self):
        return self.state.get("rssi", 0)

    def _getIP(self):
        return self.state.get("ip", "unknown")

    def _getSpeed(self):
        return self.state.get("link_speed_mbps", 0)

    def _isConnected(self):
        return self._getSpeed() != -1

    def _isWifiEnabled(self):
        ss = self.state.get("supplicant_state", "UNINITIALIZED")
        return ss != "UNINITIALIZED"

    def _wifiIcon(self):
        if self._isWifiEnabled():
            if self._isConnected():
                ico = WIFI_ICON_FILE_PREFIX + \
                      WIFI_ICON_FILE_CONNECTED_INFIX + \
                      self._getSignalAproxStrength() + \
                      WIFI_ICON_FILE_EXTENSION
            else:
                ico = WIFI_ICON_FILE_PREFIX + \
                      WIFI_ICON_FILE_DISCONNECTED_INFIX + \
                      WIFI_ICON_FILE_EXTENSION
        else:
            ico = WIFI_ICON_FILE_PREFIX + \
                  WIFI_ICON_FILE_DISABLED_INFIX + \
                  WIFI_ICON_FILE_EXTENSION
        if ico not in self.icons:
            png = Image.open(ico)
            self.icons[ico] = png
        else:
            png = self.icons[ico]
        return png

    def _toggleWifi(self):
        par = "false" if self._isWifiEnabled() else "true"
        subprocess.Popen([WIFI_ENABLE_CMD, par])
        self.state["supplicant_state"] = "UNINITIALIZED" if par == "false" else "DISCONNECTED"
        self._iconUpdate()

    def _iconUpdate(self):
        self.icon.icon = self._wifiIcon()
        self.icon.menu = self._generateMenu()
        self.icon.update_menu()

    def _generateMenu(self):
        menu_info = pystray.Menu(lambda: (
                          pystray.MenuItem(
                              f"{i}: {self.state[i]}",
                              lambda: None
                          )
                          for i in list(self.state)))
        menu = pystray.Menu(
            pystray.MenuItem(
                "Toggle Wi-Fi",
                lambda ico, it: self._toggleWifi(),
                checked=lambda it: self._isWifiEnabled()
                ),
            pystray.MenuItem(
                "Connection info",
                menu_info),
            pystray.MenuItem(
                "Quit",
                lambda: exit(0)
                )
            )
        return menu
