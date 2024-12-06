
from paho.mqtt import client as mqtt_client
import reactivex as rx
from reactivex import operators as ops
import json


def mqtt_observable( topic: str):
    client = mqtt_client.Client()
    broker = '192.168.0.11'
    port = 1883
    def observable(observer, _):

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print(f"Failed to connect, return code {rc}")

        def on_disconnect(client, userdata, rc):
            if rc != 0:
                print("Unexpected disconnection from MQTT broker")

        def on_message(client, userdata, msg):
            # Push received messages to the observer
            observer.on_next(msg.payload.decode())
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect

        client.connect(broker, port, 60)


    # Start MQTT loop in a separate thread
        client.loop_start()
        client.subscribe(topic=topic)
        client.message_callback_add(sub=topic, callback=on_message)

        def dispose():
            client.unsubscribe(topic=topic)
            client.message_callback_remove(sub=topic)
            client.loop_stop()
            client.disconnect()
            print("Disposing mqtt observable...")

        return dispose

    # Return the observable
    return rx.create(observable)
