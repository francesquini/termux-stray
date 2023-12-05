import pystray
from PIL import Image
import json
import subprocess
from ifconfigparser import IfconfigParser

exec(open('config.py').read())

class NetworkStatus:
    def __init__(self):
        self.wifiState = {}
        self.networkState = None

    def updateState(self):
        def updateWifiState():
            vout = subprocess.run([WIFI_CMD],stdout=subprocess.PIPE).stdout
            self.wifiState = json.loads(vout.decode('utf-8'))
        def updateEthernetState():
            vout = subprocess.run([ETHERNET_IFCONFIG_COMMAND, "-a"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL).stdout
            self.networkState = IfconfigParser(console_output=vout.decode('utf-8'))

        updateWifiState()
        updateEthernetState()

    def handleCommand(self, command):
        #There are no commands associated with network status
        return None

    def getNetworkInterfaces(self):
        self.networkState.list_interfaces()

    #######################
    # Wi-Fi related queries
    #######################

    def getAvailableWifiInterfaces(self):
        if not self.networkState:
            return []
        return list(filter(lambda ifce: ifce.startswith("wlan"),
                           self.networkState.list_interfaces()))

    def isWifiConnected(self):
        return self.getWifiSpeed() != -1

    def getWifiSignalStrength(self):
        return self.wifiState.get("rssi", 0)

    def getWifiSignalAproxStrength(self):
        rssi = self.getWifiSignalStrength()
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

    def getWifiIP(self):
        return self.wifiState.get("ip", "unknown")

    def getWifiSpeed(self):
        return self.wifiState.get("link_speed_mbps", 0)

    def isWifiEnabled(self):
        ss = self.wifiState.get("supplicant_state", "UNINITIALIZED")
        return ss != "UNINITIALIZED"

    def getWifiState(self):
        return self.wifiState

    ##################
    # Ethernet queries
    ##################
    def getAvailableEthernetInterfaces(self):
        if not self.networkState:
            return []
        return list(filter(lambda ifce: ifce.startswith("eth"),
                           self.networkState.list_interfaces()))

    def isEthernetConnected(self):
        #If not connected, the inteface does not even show up
        return bool(self.getAvailableEthernetInterfaces())


class NetworkStray:
    def __init__(self, netState):
        self.netState = netState
        self.stIcon = None
        self.icons = {}

    def start(self):
        self.icon = pystray.Icon(
                "Termux Network Status",
                title="Network",
                menu=self._generateMenu()
            )
        self.icon.icon = self._currentIcon()
        self.icon.run()

    def updateState(self):
        self._iconUpdate()

    def handleCommand(self, command):
        #There are no commands associated with wifi
        return None

    def _currentIcon(self):
        if self.netState.isEthernetConnected():
            #eth online
            ico = ETHERNET_ICON_FILE_PREFIX + ETHERNET_ICON_FILE_EXTENSION
        else:
            #wifi
            if self.netState.isWifiEnabled():
                if self.netState.isWifiConnected():
                    ico = WIFI_ICON_FILE_PREFIX                    + \
                        WIFI_ICON_FILE_CONNECTED_INFIX             + \
                        self.netState.getWifiSignalAproxStrength() + \
                        WIFI_ICON_FILE_EXTENSION
                else:
                    ico = WIFI_ICON_FILE_PREFIX             + \
                          WIFI_ICON_FILE_DISCONNECTED_INFIX + \
                          WIFI_ICON_FILE_EXTENSION
            else:
                ico = WIFI_ICON_FILE_PREFIX         + \
                      WIFI_ICON_FILE_DISABLED_INFIX + \
                      WIFI_ICON_FILE_EXTENSION

        if ico not in self.icons:
            png = Image.open(ico)
            self.icons[ico] = png
        else:
            png = self.icons[ico]
        return png


    def _iconUpdate(self):
        self.icon.icon = self._currentIcon()
        self.icon.menu = self._generateMenu()
        self.icon.update_menu()


    def _toggleWifi(self):
        par = "false" if self.netState.isWifiEnabled() else "true"
        subprocess.Popen([WIFI_ENABLE_CMD, par])
        self.netState.wifiState["supplicant_state"] = "UNINITIALIZED" if par == "false" else "DISCONNECTED"
        self._iconUpdate()


    def _generateMenu(self):

        def menuForInterface(inf):
            ns = self.netState.networkState
            if not ns:
                return pystray.Menu(pystray.MenuItem("Loading", None))
            else:
                nif = self.netState.networkState.get_interface(inf)._asdict()
                cnif = {k: v for k, v in nif.items() if v is not None}
                itens = [pystray.MenuItem("Connection Info:", None)] + \
                  list(pystray.MenuItem(
                          f"\t{k}: {cnif[k]}",
                          None
                   ) for k in list(cnif))
                return pystray.Menu(lambda: itens)

        def ifsMenus(ifs, txt):
            if ifs:
                return [pystray.MenuItem(f"{txt}", None)] + \
                     list(pystray.MenuItem(
                          f"\t{i}",
                          menuForInterface(i)
                     ) for i in ifs)
            else:
                return []

        def ethMenus():
            return ifsMenus(self.netState.getAvailableEthernetInterfaces(), "Ethernet (Connected)")

        def wifiMenus():
            return ifsMenus(self.netState.getAvailableWifiInterfaces(), "Additional Info")

        def wifiInfoMenu():
            termuxInfoSubMenu = pystray.Menu(lambda: list(pystray.MenuItem(
                           f"{i}: {self.netState.getWifiState()[i]}",
                           None
                          ) for i in list(self.netState.getWifiState())))
            return [pystray.MenuItem("Connection Info (Termux)", termuxInfoSubMenu),
                    pystray.Menu.SEPARATOR] + \
                    wifiMenus()

        def wifiMenu():
            toggle = [pystray.MenuItem(
                        "Toggle Wi-Fi",
                        lambda ico, it: self._toggleWifi(),
                        checked=lambda it: self.netState.isWifiEnabled()),
                     pystray.Menu.SEPARATOR
                     ]

            info = [pystray.MenuItem("Not Connected", None)] \
              if not self.netState.isWifiConnected() else wifiInfoMenu()

            menu_it = pystray.Menu(lambda: toggle + info)
            return pystray.MenuItem("WiFi", menu_it)

        menu = pystray.Menu(lambda:
                              ethMenus() +
                              [pystray.Menu.SEPARATOR,
                               wifiMenu(),
                               pystray.Menu.SEPARATOR,
                               pystray.MenuItem(
                                 "Quit",
                                 lambda: exit(0)
                               )]
                            )
        return menu
