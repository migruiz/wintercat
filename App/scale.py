
from paho.mqtt import client as mqtt_client
import reactivex as rx
import mqttObservable
from reactivex import operators as ops
import json

def scale_observable():

    SCALE_TOPIC ="WINTERCAT/house/presence"
    return mqttObservable.mqtt_observable(topic=SCALE_TOPIC).pipe(
        ops.map(lambda x: x == "ON"),
        ops.map(lambda x: {"type": "scale", "value": x})
    )

