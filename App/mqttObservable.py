
from paho.mqtt import client as mqtt_client
import reactivex as rx
from reactivex import operators as ops
import json


def mqtt_observable(client:mqtt_client.Client, topic:str):
    def observable(observer, _):

        def on_message(client, userdata, msg):
            # Push received messages to the observer
            observer.on_next(msg.payload.decode())

        client.subscribe(topic=topic)
        client.message_callback_add(sub=topic, callback=on_message)

        def dispose():
            client.unsubscribe(topic=topic)
            client.message_callback_remove(sub=topic)
            print("Disposing mqtt observable...")


        return dispose

    # Return the observable
    return rx.create(observable)
