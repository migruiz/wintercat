
from paho.mqtt import client as mqtt_client
import reactivex as rx
import mqttObservable
from reactivex import operators as ops
import json

def scale_observable(client:mqtt_client.Client):

    SCALE_TOPIC ="zigbee2mqtt/0x04cd15fffe58b077"
    return mqttObservable.mqtt_observable(client=client, topic=SCALE_TOPIC).pipe(
        ops.map(lambda x: {"type": "scale", "value": x["value"] == "in"})
    )

