
from paho.mqtt import client as mqtt_client
import reactivex as rx
from reactivex import operators as ops
import json


def get_mqtt_client_observable():
    client = mqtt_client.Client()
    broker = '192.168.0.11'
    port = 1883
    def observable(observer, _):

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                observer.on_next(client)
            else:
                print(f"Failed to connect, return code {rc}")

        def on_disconnect(client, userdata, rc):
            if rc != 0:
                print("Unexpected disconnection from MQTT broker")

        
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect

        client.connect(broker, port, 60)


    # Start MQTT loop in a separate thread
        client.loop_start()

        def dispose():
            client.loop_stop()
            client.disconnect()
            print("Disposing mqtt Client observable...")

        return dispose

    # Return the observable
    return rx.create(observable)
