import random
import sys
import reactivex as rx
from reactivex import operators as ops
import time
from datetime import datetime


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


input_observable = InputObservable().pipe(ops.map(lambda x : {"type":"master", "state":x}))
#subscription = input_observable.subscribe(lambda value: print(f"Received: {value}"))

timer = rx.interval(5).pipe(ops.map(lambda x : {"type":"timer"}))
#timer.subscribe(lambda value: print(f"Received: {value}"))

comb = rx.merge(timer,input_observable)
#comb.subscribe(lambda value: print(f"Received: {value}"))

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
            return {**acc, 'master': False, 'heating': False}
    
comb1 = comb.pipe(
   ops.scan(buildCurrent, {"master":False, "heating":False}))

comb1.subscribe(lambda x: print("Master:{0} Heating:{1}".format(x["master"],x["heating"])))

#ob = rx.timer(duetime= datetime.now(),period=3)
#ob.subscribe(lambda value: print(f"Received: {value}"))


try:
    # Keep the program running indefinitely
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    #subscription.dispose()
    print("Observer stopped")
