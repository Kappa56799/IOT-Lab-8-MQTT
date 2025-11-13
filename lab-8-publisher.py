import umqtt.robust as umqtt
from network import WLAN
from machine import ADC, Timer
import time
import socket


# ---------- Wi-Fi Connection ----------
def connect(wifi_obj, ssid, password, timeout=10):
    """
    Attempts to connect to the specified Wi-Fi network within a timeout.
    Returns True if successful, False otherwise.
    """
    wifi_obj.connect(ssid, password)
    while timeout > 0:
        if wifi_obj.status() != 3:  # 3 = connected
            time.sleep(1)
            timeout -= 1
        else:
            print("Connected to Wi-Fi")
            return True
    return False

def read_temp_send_data(timer):
    global sensor_temp

    # Read raw analog sensor data
    value = sensor_temp.read_u16()
    voltage = value * (3.3 / 2**16)
    temperature = 27 - (voltage - 0.706) / 0.001721

    mqtt.publish(TOPIC, str(temperature).encode())
    
    
# ---------- Periodic Temperature Sender ----------
temp_timer = Timer()
temp_timer.init(period=2000, mode=Timer.PERIODIC, callback=read_temp_send_data)

ssid = "Ya"
password = "12345678"

HOSTNAME = "172.20.10.14"
PORT = 1883
TOPIC = "temp/pico"

sensor_temp = ADC(4)  # Internal temperature sensor
conversion_factor = 0.706  # Approximate reference voltage

wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

if connect(wifi, ssid, password):
    print("Wifi connected")
    
    mqtt = umqtt.MQTTClient(
        client_id= b"publish", server=HOSTNAME.encode(), port=PORT, keepalive=7000
    )

    mqtt.connect()
    
    while True:
        time.sleep(1)
else:
    print("Wi-fi connection failed.")