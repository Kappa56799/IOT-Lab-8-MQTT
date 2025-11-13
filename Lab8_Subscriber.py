import umqtt.robust as umqtt
from network import WLAN
import machine, time
from machine import Pin, PWM, ADC, Timer


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


ssid = "Ya"
password = "12345678"

wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

if not connect(wifi, ssid, password):
    print("Wi-Fi connection failed.")

# Assuming that you connect to the internet as normal...

HOSTNAME = "172.20.10.14"
PORT = 1883
TOPIC = "temp/pico"

mqtt = umqtt.MQTTClient(
    client_id=b"subscriber",
    server=HOSTNAME.encode(),
    port=PORT,
    keepalive=7000,  # seconds
)

# Use built-in LED
led = Pin("LED", Pin.OUT)


def callback(topic, message):
    # TODO Ignore messages that are not part of
    # the temp/pico topic
    topic = topic.decode()
    message = message.decode()

    # execute only if topic is 'temp/pico'
    if topic == TOPIC:

        print(f"Temperature received: {message}")

        # if message recieved and message (temp) is greater than 30 led comes on
        # else led off
        if float(message) > 30:
            led.value(1)
        else:
            led.value(0)

    else:
        print(f"Ignored message on topic: {topic}")


# Assuming that you have the temperature as an int or a
# float in a variable called `temp`:
mqtt.set_callback(callback)
mqtt.connect()
mqtt.subscribe(TOPIC.encode())
print(f"Subscribed to topic: {TOPIC}")
# Blocking wait
# -- use .check_msg() for non-blocking

while True:
    mqtt.wait_msg()
