import scheduler
import scale
import random
import reactivex as rx
from reactivex import operators as ops
import time
from paho.mqtt import client as mqtt_client

# MQTT Broker Config
broker = '192.168.0.11'
port = 1883


# Create MQTT client
mqtt_client = mqtt_client.Client()
mqtt_client.connect(broker, port, 60)


class InputObservable(rx.Observable):
    def __init__(self):
        super().__init__(self._subscribe)

    def _subscribe(self, observer, scheduler = None):
        while True:
            seconds = random.randrange(1,10)
            if (seconds % 2) == 0:
                observer.on_next(True)
            else:
                observer.on_next(False)
            time.sleep(seconds)


input_observable = InputObservable().pipe(ops.map(lambda x: {"type":"master", "value":x }))

on_cron_observable = scheduler.cron_observable("14:40",True).pipe(ops.map(lambda x: {"type":"cron_on", "state":x }))
off_cron_observable = scheduler.cron_observable("14:45",False).pipe(ops.map(lambda x: {"type":"cron_off", "state":x }))

merged_cron_observable = rx.merge(on_cron_observable,off_cron_observable)

#{"Last":False, "New":False}}
def buildCronInput(acc,curr):
    return {**acc, 'Last': acc["New"], 'New': curr["state"]}

cron_stream = merged_cron_observable.pipe(
   ops.scan(buildCronInput, {"Last":False, "New":False}),
   ops.map(lambda x : {"type": "cron","value": x["New"]})
   )

#scale observable
scale_observable = scale.scale_observable(mqtt_client)
scale_stream = scale_observable.pipe( ops.map(lambda x : {"type": "scale","value": True if x["value"] == "in" else False}))
#subscription = scale_stream.subscribe(lambda x: print("Type:{0}".format(x)))

final_observable = rx.merge(cron_stream, scale_stream)

subscription = final_observable.subscribe(lambda x: print("Type:{0} Value:{1}".format(x["type"],x["value"])))


try:
    # Keep the program running indefinitely
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    mqtt_client.disconnect()
    subscription.dispose()
    print("Observer stopped")