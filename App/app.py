from dotenv import load_dotenv
import control
import time
import reactivex as rx
from reactivex import operators as ops
from paho.mqtt import client as mqtt_client
import mqttClientObservable
import json
import scheduler
import scale
import os

load_dotenv()

TEMP_SETTING = int(os.environ.get("TEMP_SETTING") or 30) 
CRON_ON_TIME = os.environ.get("CRON_ON_TIME") or "18:00"
CRON_OFF_TIME = os.environ.get("CRON_OFF_TIME") or "09:00"
SCALE_ENABLE = bool(
    os.getenv("SCALE_ENABLE", 'False').lower() in ('true', '1')) or False
CRON_ENABLE = bool(os.getenv("CRON_ENABLE", 'False').lower() in ('true', '1')) 

print(f'TEMP_SETTING {TEMP_SETTING}')
print(f'CRON_ON_TIME {CRON_ON_TIME}')
print(f'CRON_OFF_TIME {CRON_OFF_TIME}')
print(f'SCALE_ENABLE {SCALE_ENABLE}')
print(f'CRON_ENABLE {CRON_ENABLE}')

def get_app_observable(client: mqtt_client.Client):

    control_observable = control.control_observable(client)

    cron_observable = scheduler.cron_observable(onTime=CRON_ON_TIME, offTime=CRON_OFF_TIME).pipe(
        ops.filter(lambda _: CRON_ENABLE))

    scale_stream = scale.scale_observable(client).pipe(
        ops.filter(lambda _: SCALE_ENABLE))

    def get_ON_switching_obs():
        return rx.interval(1 * 60).pipe(
            ops.start_with(1),
            ops.scan(accumulator=lambda acc, _: acc +
                     1 if acc < 60 else 1, seed=0),
            ops.map(lambda x: x <= TEMP_SETTING)
        )
        
    def get_OFF_switching_obs():
        return rx.interval(1 * 60).pipe(
            ops.start_with(False),
            ops.map(lambda _: False)
        )

    return rx.merge(control_observable, scale_stream, cron_observable).pipe(
        ops.distinct_until_changed(),
        ops.do_action(lambda x: print(f"Setting Control to : {x}")),
        ops.map(lambda x: get_ON_switching_obs() if x["value"] else get_OFF_switching_obs()),
        ops.switch_latest()
    )


def publish(client:mqtt_client.Client, msg):   
    client.publish("WINTERCAT/operate", json.dumps(
        {"messageType": "heatRelay", "value": msg}))
    print(f"Relay set to : {msg}")


obs = mqtt_client_observable = mqttClientObservable.get_mqtt_client_observable().pipe(
    ops.flat_map(lambda c: get_app_observable(client=c).pipe(
        ops.map(lambda msg: {"client": c, "msg": msg})
    )),

)

subscription = obs.subscribe(
    on_next=lambda e: publish(client=e["client"], msg=e["msg"]),
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
    subscription.dispose()

    print("Subscription disposed and program terminated.")
