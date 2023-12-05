PLUGGED_UPDATE_INTERVAL=20
UNPLUGGED_UPDATE_INTERVAL=60
BATTERY_THROTTLE_ENABLE=True

CONTROL_PIPE_PATH="termux-stray-control-pipe"

LOGGING_ENABLED=True

##############################
# Volume Systray Configuration
##############################

VOLUME_SYSTRAY_ENABLE=True
VOLUME_DEFAULT_STREAM="music"
VOLUME_MUTE_TOGGLE_DEFAULT_VOLUME=8

VOLUME_CMD="/data/data/com.termux/files/usr/bin/termux-volume"

VOLUME_ICON_MUTED_FILE_PATH="./icons/audio-volume-muted.png"
VOLUME_ICON_LOW_FILE_PATH="./icons/audio-volume-low.png"
VOLUME_ICON_MEDIUM_FILE_PATH="./icons/audio-volume-medium.png"
VOLUME_ICON_HIGH_FILE_PATH="./icons/audio-volume-high.png"


###############################
# Battery Systray Configuration
###############################

BATTERY_SYSTRAY_ENABLE=True
BATTERY_DEDICATED_PLUGGED_IN_ICON=True

BATTERY_CMD="/data/data/com.termux/files/usr/bin/termux-battery-status"

BATTERY_ICON_FILE_PREFIX="./icons/battery-"
BATTERY_ICON_CHARGING_SUFFIX="-charging"
BATTERY_ICON_FILE_EXTENSION=".png"

BATTERY_ICON_ON_AC_ADAPTER="./icons/battery-ac-adapter.png"


#######################
# Network configuration
#######################

NETWORK_SYSTRAY_ENABLE=True

############################
# WiFi Systray Configuration
############################

WIFI_CMD="/data/data/com.termux/files/usr/bin/termux-wifi-connectioninfo"
WIFI_ENABLE_CMD="/data/data/com.termux/files/usr/bin/termux-wifi-enable"

WIFI_ICON_FILE_PREFIX="./icons/network-wireless-"
WIFI_ICON_FILE_CONNECTED_INFIX="signal-"
WIFI_ICON_FILE_DISCONNECTED_INFIX="offline"
WIFI_ICON_FILE_DISABLED_INFIX="disabled"
WIFI_ICON_FILE_EXTENSION=".png"
WIFI_ICON_EXCELLENT_THOLD=-30
WIFI_ICON_GOOD_THOLD=-45
WIFI_ICON_OK_THOLD=-70
WIFI_ICON_LOW_THOLD=-80

################################
# Ethernet Systray Configuration
################################

ETHERNET_IFCONFIG_COMMAND="/data/data/com.termux/files/usr/bin/ifconfig"
ETHERNET_ICON_FILE_PREFIX="./icons/network-wired"
ETHERNET_ICON_FILE_EXTENSION=".png"
