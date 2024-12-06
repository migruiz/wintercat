
from paho.mqtt import client as mqtt_client
import reactivex as rx
from reactivex import operators as ops
import json


def control_observable():
    client = mqtt_client.Client()
    broker = '192.168.0.11'
    port = 1883

    def observable(observer, _):

        def on_message(client, userdata, msg):
            # Push received messages to the observer
            observer.on_next(json.loads(msg.payload.decode()))

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                observer.on_error(
                    Exception(f"Failed to connect, return code {rc}"))

        def on_disconnect(client, userdata, rc):
            if rc != 0:
                print("Unexpected disconnection from MQTT broker")

        # Set up MQTT callbacks
        client.on_message = on_message
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect

        # Connect to the broker
        try:
            client.connect(broker, port, 60)
        except Exception as e:
            observer.on_error(e)
            return

        # Subscribe to the topic
        client.subscribe("zigbee2mqtt/0x04cd15fffe58b077")

        # Start MQTT loop in a separate thread
        client.loop_start()

        def dispose():
            print("Disposing CONTROL observable...")
            client.loop_stop()
            client.disconnect()

        # Return dispose method to clean up resources
        return dispose

    # Return the observable
    return rx.create(observable).pipe(
        ops.filter(lambda x: (x["action"] == "brightness_move_up" or x["action"] ==
                   "on" or x["action"] == "brightness_move_down" or x["action"] == "off")),
        ops.map(lambda x: x["action"] ==
                "brightness_move_up" or x["action"] == "on"),
        ops.map(lambda x: {"type": "master", "value": x})
    )