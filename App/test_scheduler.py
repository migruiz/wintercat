import scheduler
import random
import reactivex as rx
from reactivex import operators as ops
import time

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


input_observable = InputObservable().pipe(ops.map(lambda x: {"type":"master", "state":x }))

on_cron_observable = scheduler.cron_observable("11:31",True).pipe(ops.map(lambda x: {"type":"cron_on", "state":x }))
off_cron_observable = scheduler.cron_observable("11:33",False).pipe(ops.map(lambda x: {"type":"cron_off", "state":x }))

merged_cron_observable = rx.merge(on_cron_observable,off_cron_observable)

#{"Last":False, "New":False}}
def buildCronInput(acc,curr):
    return {**acc, 'Last': acc["New"], 'New': curr["state"]}

cron_stream = merged_cron_observable.pipe(
   ops.scan(buildCronInput, {"Last":False, "New":False}))

#Next combine cron_stream with input observable(mqtt_observable mock)

subscription = cron_stream.subscribe(lambda x: print("Last:{0} New:{1}".format(x["Last"],x["New"])))


try:
    # Keep the program running indefinitely
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    subscription.dispose()
    print("Observer stopped")