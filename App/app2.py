from dotenv import load_dotenv
import control
import time
import reactivex as rx
from reactivex import operators as ops
from paho.mqtt import client as mqtt_client
import json
import scheduler
import scale
import os

load_dotenv()

TEMP_SETTING = int(os.environ.get("TEMP_SETTING"))
CRON_ON_TIME = os.environ.get("CRON_ON_TIME")
CRON_OFF_TIME = os.environ.get("CRON_OFF_TIME")
SCALE_ENABLE = bool(
    os.getenv("SCALE_ENABLE", 'False').lower() in ('true', '1'))
CRON_ENABLE = bool(os.getenv("CRON_ENABLE", 'False').lower() in ('true', '1'))


# Create the master switch Observable
mqtt_stream = control.control_observable()

# Filter master switch observable
filtered_input_stream = mqtt_stream.pipe(ops.filter(lambda x: (x["action"] == "brightness_move_up" or x["action"] == "on" or x["action"] == "brightness_move_down" or x["action"] == "off")),
                                         ops.map(
                                             lambda x: x["action"] == "brightness_move_up" or x["action"] == "on")
                                         )

# Input stream
input_stream = filtered_input_stream.pipe(
    ops.map(lambda x: {"type": "master", "value": x})
)

# Create cron observables
on_cron_observable = scheduler.cron_observable(CRON_ON_TIME).pipe(
    ops.map(lambda x: {"type": "cron", "value": True}))
off_cron_observable = scheduler.cron_observable(CRON_OFF_TIME).pipe(
    ops.map(lambda x: {"type": "cron", "value": False}))


def filter_cron(x):
    if (CRON_ENABLE):
        return x


# Merging cron observables
cron_observable = rx.merge(on_cron_observable, off_cron_observable).pipe(
    ops.filter(lambda _: CRON_ENABLE))


scale_stream = scale.scale_observable().pipe(
    ops.map(lambda x: {"type": "scale", "value": x["value"] == "in"}),
    ops.filter(lambda _: SCALE_ENABLE))


final_observable = rx.merge(input_stream, scale_stream, cron_observable)


def get_switching_obs():
    return rx.interval(10 * 60).pipe(
        ops.start_with(1),
        ops.scan(accumulator=lambda acc, _: acc + 1 if acc < 6 else 1, seed=0),
        ops.map(lambda x: x <= TEMP_SETTING)
    )


observablesStream = final_observable.pipe(
    ops.map(lambda x: get_switching_obs() if x["value"] else rx.of(False)))

swi = observablesStream.pipe(ops.switch_latest())


def publish(on_off_status):
    print(f"Received message: {on_off_status}")
    # mqtt_client.publish("WINTERCAT/test", json.dumps(
   #     {"messageType": "heatRelay", "value": on_off_status}))


# Subscribe to the observable
subscription = swi.subscribe(
    on_next=lambda x: publish(x),
    on_error=lambda e: print(f"Error occurred: {e}"),
    on_completed=lambda: print("Stream completed!")
)

try:
    # Keep the program running to receive messages
    print("Press CTRL+C to exit...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    mqtt_client.disconnect()
    subscription.dispose()
    print("Subscription disposed and program terminated.")
