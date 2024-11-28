import masterzigbee
import time
import reactivex as rx
from reactivex import operators as ops

# Create the MQTT Observable
mqtt_stream = masterzigbee.mqtt_observable()

# Filter MQTT stream
filtered_stream = mqtt_stream.pipe(ops.filter(lambda x: (x["action"] == "brightness_move_up" or x["action"] == "on" or x["action"] == "brightness_move_down" or x["action"] == "off")),
                                   ops.map(lambda x: x["action"] == "brightness_move_up" or x["action"] == "on")) 

# Subscribe to the observable
subscription = filtered_stream.subscribe(
    on_next = lambda x: print(f"Received message: {x}"),
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