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








def get_mqtt_client():
    client = mqtt_client.Client()
    broker = '192.168.0.11'
    port = 1883

    def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
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
    return client





client  = get_mqtt_client()





try:
    # Keep the program running to receive messages
    print("Press CTRL+C to exit...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.loop_stop()
    client.disconnect()
    print("Subscription disposed and program terminated.")






exit()

control_observable = control.control_observable()

cron_observable = scheduler.cron_observable(onTime=CRON_ON_TIME, offTime=CRON_OFF_TIME).pipe(
    ops.filter(lambda _: CRON_ENABLE))

scale_stream = scale.scale_observable().pipe(
    ops.filter(lambda _: SCALE_ENABLE))


def get_switching_obs():
    return rx.interval(1 * 60).pipe(
        ops.start_with(1),
        ops.scan(accumulator=lambda acc, _: acc +
                 1 if acc < 60 else 1, seed=0),
        ops.map(lambda x: x <= TEMP_SETTING)
    )


observablesStream = rx.merge(control_observable, scale_stream, cron_observable).pipe(
    ops.map(lambda x: get_switching_obs() if x["value"] else rx.of(False)),
    ops.switch_latest()
)


def publish(on_off_status):
    print(f"Received message: {on_off_status}")
    # mqtt_client.publish("WINTERCAT/test", json.dumps(
   #     {"messageType": "heatRelay", "value": on_off_status}))


# Subscribe to the observable
subscription = observablesStream.subscribe(
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
