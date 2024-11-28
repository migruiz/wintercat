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
translation = rx.create(push_number_message)
readingsSource = translation.pipe(ops.filter(lambda x: x["messageType"] == "number" or x["messageType"] == "letter" ),ops.share())

#subscription = readingsSource.subscribe(lambda x: print("The element is {0}".format(x)))

def calculateCurrent(acc,curr):
    if curr["messageType"] == "number":
        return {**acc, 'number': curr["value"]}
    else:
        return {**acc, 'letter': curr["value"]}

comb1 = readingsSource.pipe(
   ops.scan(calculateCurrent, {"number":0, "letter":''}))
#subscription = comb1.subscribe(lambda x: print("The element is {0}".format(x)))

# Subscribe to the stream
subscription = comb1.subscribe(
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
    translation.dispose()