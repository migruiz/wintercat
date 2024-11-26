from paho.mqtt import client as mqtt_client
import random
import sys
import reactivex as rx
from reactivex import operators as ops
import time
import json


broker = '192.168.0.11'
port = 1883
topic = "testtopic/numbers"
client_id = f'python-mqtt-{random.randint(0, 1000)}'


def push_number_message(observer, scheduler):
    client = mqtt_client.Client()

    def message_handling(client, userdata, msg):
        observer.on_next(json.loads(msg.payload.decode()))

    client.on_message = message_handling

    try:
        if client.connect(broker, port, 60) != 0:
            print("Couldn't connect to the MQTT broker")
            observer.on_error("Connection failed")
            return

        client.subscribe(topic)
        client.loop_start()

        print("Press CTRL+C to exit...")
        while True:
            time.sleep(1)  # Keep the loop alive

    except Exception as e:
        print(f"Exception occurred: {e}")
        observer.on_error(e)

    finally:
        print("Disconnecting from the MQTT broker")
        client.loop_stop()
        client.disconnect()

# Create a reactive stream
source = rx.create(push_number_message)
result = source.pipe(ops.map(lambda x: x["msg"]))

# Subscribe to the stream
subscription = result.subscribe(
    lambda x: print(f"The element is {x}"),
    lambda e: print(f"Error: {e}"),
    lambda: print("Completed")
)

try:
    # Keep the program running
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("Stopping observer...")
    subscription.dispose()
    source.dispose()