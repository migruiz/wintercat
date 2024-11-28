import masterzigbee
import time

# Create the MQTT Observable
mqtt_stream = masterzigbee.mqtt_observable()

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