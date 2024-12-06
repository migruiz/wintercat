
from paho.mqtt import client as mqtt_client
import reactivex as rx
from reactivex import operators as ops
import json


def control_observable(client:mqtt_client.Client):

    def observable(observer, _):

        def on_message(client, userdata, msg):
            # Push received messages to the observer
            observer.on_next(json.loads(msg.payload.decode()))



        # Set up MQTT callbacks
        client.on_message = on_message


        # Subscribe to the topic
        client.subscribe("zigbee2mqtt/0x04cd15fffe58b077")



        def dispose():
            print("Disposing CONTROL observable...")


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
