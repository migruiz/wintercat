
from paho.mqtt import client as mqtt_client
import reactivex as rx
import json

def mqtt_observable(client):
    
    topic = "zigbee2mqtt/0x04cd15fffe58b077"
    def observable(observer, _):

        def on_message(client, userdata, msg):
            # Push received messages to the observer
            observer.on_next(json.loads(msg.payload.decode()))

        # Set up MQTT callbacks
        client.on_message = on_message

        # Subscribe to the topic
        client.subscribe(topic)

        # Start MQTT loop in a separate thread
        client.loop_start()

        def dispose():
            print("Disposing MQTT observable...")
            client.loop_stop()

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
