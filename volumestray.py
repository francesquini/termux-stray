import pystray
from PIL import Image
import json
import subprocess

exec(open('config.py').read())

VOLUME_ICON_MUTED= Image.open(VOLUME_ICON_MUTED_FILE_PATH)
VOLUME_ICON_LOW= Image.open(VOLUME_ICON_LOW_FILE_PATH)
VOLUME_ICON_MEDIUM= Image.open(VOLUME_ICON_MEDIUM_FILE_PATH)
VOLUME_ICON_HIGH= Image.open(VOLUME_ICON_HIGH_FILE_PATH)

class VolumeStray:
    def __init__(self):
        self.state = {}
        self.stream = VOLUME_DEFAULT_STREAM
        self.icon = None
        self.muted = False
        self.last_before_mute = 0

    def start(self):
        self.icon = pystray.Icon(
                "Termux Volume Control",
                title="Volume",
                menu=self._generateMenu()
            )
        self.icon.icon = self._volumeIcon(self.stream)
        self.icon.run()

    def updateState(self):
        vout = subprocess.run([VOLUME_CMD], stdout=subprocess.PIPE).stdout
        nstate = {}
        for d in json.loads(vout.decode('utf-8')):
            nstate[d["stream"]] = d
        if self.state != nstate:
            self.state = nstate
            self._iconUpdate()

    def handleCommand(self, command):
        def volume_change(ncv):
            subprocess.Popen([VOLUME_CMD, self.stream, str(ncv)])
            self.state[self.stream]["volume"] = ncv
            self._iconUpdate()
            (cv, mv, p) = self._volumeStatus(self.stream)
            self.icon.notify(f"Current:{cv} Max:{mv}", f"{self.stream}: {round(p * 100)}%")

        def volume_increase_action():
            if self.muted:
                volume_mute_action()
            else:
                (cv, vm, _) = self._volumeStatus(self.stream)
                ncv = cv + 1
                if ncv > vm:
                    print(f"Cannot increase volume (<{self.stream}> maxed out: {cv}/{vm}).")
                else:
                    print (f"Increasing <{self.stream}> volume {cv}->{ncv}")
                    volume_change(ncv)

        def volume_decrease_action():
            if self.muted:
                volume_mute_action()
            else:
                cv = self._volumeStatus(self.stream)[0]
                ncv = cv - 1
                if ncv < 0:
                    print(f"Cannot decrease volume (<{self.stream}> already mute: {cv}).")
                else:
                    print (f"Decreasing <{self.stream}> volume {cv}->{ncv}")
                    volume_change(ncv)


        def volume_mute_action():
            # Check if toggle mute
            if self.muted:
                print("Toggling mute")
                self.muted = False
                volume_change(self.last_before_mute)
            else:
                cv = self._volumeStatus(self.stream)[0]
                if cv == 0:
                    # Muted, but not manually
                    print(f"Already mute <{self.stream}>. Toggling to default.")
                    # Unmute to default volume
                    volume_change(VOLUME_MUTE_TOGGLE_DEFAULT_VOLUME)
                else:
                    print (f"Muting <{self.stream}> volume {cv}->0")
                    self.muted = True
                    self.last_before_mute = cv
                    volume_change(0)


        match command:
            case "TermuxStrayIncreaseVolume":
                return volume_increase_action
            case "TermuxStrayDecreaseVolume":
                return volume_decrease_action
            case "TermuxStrayMuteVolume":
                return volume_mute_action
            case _:
                return None

    def _volumeStatus(self, stream):
        if stream in self.state:
            vol_dict = self.state[stream]
            v = vol_dict["volume"]
            m = vol_dict["max_volume"]
        else:
            v = 0
            m = 1
        p = v / m
        return (v, m, p)


    def _volumeRepr(self, stream):
        cv = self._volumeStatus(stream)[2]
        if cv == 0:
            return (VOLUME_ICON_MUTED,  '🔇')
        elif cv < 0.25:
            return (VOLUME_ICON_LOW,    '🔈')
        elif cv < 0.7:
            return (VOLUME_ICON_MEDIUM, '🔉')
        else:
            return (VOLUME_ICON_HIGH,   '🔊')

    def _volumeChar(self, stream):
        return self._volumeRepr(stream)[1]

    def _volumeIcon(self, stream):
        return self._volumeRepr(stream)[0]

    def _iconUpdate(self):
        self.icon.icon = self._volumeIcon(self.stream)
        self.icon.menu = self._generateMenu()
        self.icon.update_menu()

    def _generateMenu(self):
        def setStream(nstream):
            self.stream = str(nstream).split()[0]
            self._iconUpdate()

        def isCurrentStream(stream):
            return str(stream).startswith(self.stream)

        menu_stream = pystray.Menu(lambda: (
                          pystray.MenuItem(
                              f"{st : <13}\t{round((self._volumeStatus(st)[2])*100)}%",
                              lambda ico, it: setStream(it),
                              checked=lambda it: isCurrentStream(it),
                              radio=True
                          )
                          for st in list(self.state)))

        menu = pystray.Menu(
                   pystray.MenuItem(
                       f"Streams (→ {self.stream})",
                       menu_stream
                   ),
                   pystray.MenuItem(
                       "Quit",
                       lambda: exit(0)
                   )
               )
        return menu
