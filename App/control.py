
from paho.mqtt import client as mqtt_client
import reactivex as rx
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
                observer.on_error(Exception(f"Failed to connect, return code {rc}"))
        
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
    return rx.create(observable)


"""
# Create the MQTT Observable
mqtt_stream = mqtt_observable(broker, port, topic)

# Subscribe to the observable
subscription = mqtt_stream.subscribe(
    on_next = lambda x: print(f"Received message: {x[0]}: {x[1]}"),
    on_error = lambda e: print(f"Error occurred: {e}"),
    on_completed = lambda: print("Stream completed!")
)

try:
    # Keep the program running to receive messages
    print("Press CTRL+C to exit...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    subscription.dispose()
    print("Subscription disposed and program terminated.")

"""
