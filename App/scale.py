
from paho.mqtt import client as mqtt_client
import reactivex as rx
import mqttTopicObservable
from reactivex import operators as ops
import json

def scale_observable(client:mqtt_client.Client):

    SCALE_TOPIC ="WINTERCAT/house/presence"
    return mqttTopicObservable.mqtt_observable(client=client, topic=SCALE_TOPIC).pipe(
        ops.map(lambda x: x == "ON"),
        ops.map(lambda x: {"type": "scale", "value": x})
    )

