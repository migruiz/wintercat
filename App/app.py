import masterzigbee
import time
import reactivex as rx
from reactivex import operators as ops
from paho.mqtt import client as mqtt_client
import json

temp_setting = 4
# MQTT Broker Config
broker = '192.168.0.11'
port = 1883
topic = "WINTERCAT/operate"  # "zigbee2mqtt/0x94deb8fffe57b8ff"
# client_id = f'python-mqtt-{random.randint(0, 1000)}'


# Create MQTT client
mqtt_client = mqtt_client.Client()
mqtt_client.connect(broker, port, 60)

# Create the MQTT Observable
mqtt_stream = masterzigbee.mqtt_observable(mqtt_client)

# Filter MQTT stream
filtered_input_stream = mqtt_stream.pipe(ops.filter(lambda x: (x["action"] == "brightness_move_up" or x["action"] == "on" or x["action"] == "brightness_move_down" or x["action"] == "off")),
                                         ops.map(
                                             lambda x: x["action"] == "brightness_move_up" or x["action"] == "on")
                                         )


def get_switching_obs():
    return rx.interval(10 * 60).pipe(
        ops.start_with(1),
        ops.scan(accumulator=lambda acc, _: acc + 1 if acc < 6 else 1, seed=0),
        ops.map(lambda x: x <= temp_setting)
         )


observablesStream = filtered_input_stream.pipe(
    ops.map(lambda x: get_switching_obs() if x else rx.of(False)))

swi = observablesStream.pipe(ops.switch_latest())


def publish(on_off_status):
    print(f"Received message: {on_off_status}")
    mqtt_client.publish(topic, json.dumps(
        {"messageType": "heatRelay", "value": on_off_status}))


# Subscribe to the observable
subscription = swi.subscribe(
    on_next=lambda x: publish(x),
    on_error=lambda e: print(f"Error occurred: {e}"),
    on_completed=lambda: print("Stream completed!")
)

try:
    # Keep the program running to receive messages
    print("Press CTRL+C to exit...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    mqtt_client.disconnect()
    subscription.dispose()
    print("Subscription disposed and program terminated.")
