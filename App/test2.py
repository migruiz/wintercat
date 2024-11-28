from paho.mqtt import client as mqtt_client
import random
import sys
import time
import json


broker = '192.168.0.11'
port = 1883
topic = "testtopic/sonia"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

client = mqtt_client.Client()

def message_handling(client, userdata, msg):
    client.publish("testtopic/callback", "Hi, paho mqtt client works fine!", 0)
    print(f"{msg.topic}: {msg.payload.decode()}")

client.on_message = message_handling

try:
    if client.connect(broker, port, 60) != 0:
        print("Couldn't connect to the MQTT broker")

    print("Before subscribe")
    client.subscribe(topic)
    print("Before loopstart")
    client.loop_start()

    print("Press CTRL+C to exit...")
    while True:
        time.sleep(1)  # Keep the loop alive

except Exception as e:
    print(f"Exception occurred: {e}")

finally:
    print("Disconnecting from the MQTT broker")
    client.loop_stop()
    client.disconnect()