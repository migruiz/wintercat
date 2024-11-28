from paho.mqtt import client as mqtt_client
import random
import sys

broker = '192.168.0.11'
port = 1883
topic = "zigbee2mqtt/0x94deb8fffe57b8ff" #"python/mqtt"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'

client = mqtt_client.Client()

def message_handling(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")

client.on_message = message_handling

if client.connect(broker, port, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    sys.exit(1)

client.subscribe(topic)

try:
    print("Press CTRL+C to exit...")
    client.loop_forever()
except Exception:
    print("Caught an Exception, something went wrong...")
finally:
    print("Disconnecting from the MQTT broker")
    client.disconnect()