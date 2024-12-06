
from paho.mqtt import client as mqtt_client
import reactivex as rx
import mqttObservable
from reactivex import operators as ops
import json


def control_observable(client:mqtt_client.Client):
    CONTROL_TOPIC ="zigbee2mqtt/0x04cd15fffe58b077"
    return mqttObservable.mqtt_observable(client=client, topic=CONTROL_TOPIC).pipe(
        ops.filter(lambda x: (x["action"] == "brightness_move_up" or x["action"] ==
                   "on" or x["action"] == "brightness_move_down" or x["action"] == "off")),
        ops.map(lambda x: x["action"] ==
                "brightness_move_up" or x["action"] == "on"),
        ops.map(lambda x: {"type": "master", "value": x})
    )
