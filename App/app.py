import masterzigbee
import time
import reactivex as rx
from reactivex import operators as ops

timer_interval = 5

# Create the MQTT Observable
mqtt_stream = masterzigbee.mqtt_observable()

# Filter MQTT stream
filtered_input_stream = mqtt_stream.pipe(ops.filter(lambda x: (x["action"] == "brightness_move_up" or x["action"] == "on" or x["action"] == "brightness_move_down" or x["action"] == "off")),
                                   ops.map(lambda x: x["action"] == "brightness_move_up" or x["action"] == "on"),
                                   ops.map(lambda x: {"type":"master", "state":x})) 

timer = rx.interval(timer_interval).pipe(ops.map(lambda x : {"type":"timer"}))

comb = rx.merge(timer,filtered_input_stream)


#{"master":False, "heating":False}
def buildCurrent(acc,curr):
    if curr["type"] == "master":
        if curr["state"] == False:
            return {**acc, 'master': False, 'heating': False}
        else:
            return {**acc, 'master': curr["state"], 'heating': not acc["heating"]}
    else:
        if(acc["master"] == True):
            return {**acc, 'heating': not acc["heating"]}
        else:
            return {**acc,  'heating': False}

comb1 = comb.pipe(
   ops.scan(buildCurrent, {"master":False, "heating":False}))

#comb1.subscribe(lambda x: print("Master:{0} Heating:{1}".format(x["master"],x["heating"])))

# Subscribe to the observable
subscription = comb1.subscribe(
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