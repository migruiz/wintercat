import reactivex as rx
import time
import random
from reactivex import operators as ops

source = rx.of(1, 2,3,4,5,6,7,8,9,10).pipe(ops.map(lambda x: {"type":"number", 'value':x}))
source2 = rx.of("a","b","c","d","e").pipe(ops.map(lambda x: {"type" : "letter", "value" : x}))

delayedNumbers = source.pipe(ops.flat_map(lambda x:rx.of(x).pipe(ops.delay(random.randrange(0,5)))))
delayedLetters = source2.pipe(ops.flat_map(lambda x:rx.of(x).pipe(ops.delay(random.randrange(0,5)))))

res = rx.merge(delayedNumbers,delayedLetters)

def calculateCurrent(acc,curr):
    if curr["type"] == "number":
        return {"number" : curr["value"],"letter" : acc["letter"]}
    else:
        return {"number" : acc["number"],"letter" : curr["value"]}

comb1 = res.pipe(
   ops.scan(calculateCurrent, {"number":0, "letter":''}))

comb1.subscribe(lambda x: print("The element is {0} {1}".format(x["number"],x["letter"])))
while True:
    time.sleep(10)