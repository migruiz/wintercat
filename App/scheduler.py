import threading
import time
import reactivex as rx
import schedule
from reactivex import operators as ops


def run_continuously(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def create_cron_observable(execTime):

    booking = schedule.every().day.at(execTime)

    def observable(observer, _):
        def job():
            observer.on_next(1)

        stop_run_continuously = run_continuously()
        booking.do(job)

        schedule.run_pending()

        def dispose():
            print("Disposing Cron observable...")
            schedule.clear()
            stop_run_continuously.set()

        # Return dispose method to clean up resources
        return dispose

    # Return the observable
    return rx.create(observable)


def cron_observable(onTime, offTime):
    on_cron_observable = create_cron_observable(onTime).pipe(
        ops.map(lambda x: {"type": "cron", "value": True})
    )
    off_cron_observable = create_cron_observable(offTime).pipe(
        ops.map(lambda x: {"type": "cron", "value": False})
    )
    return rx.merge(on_cron_observable, off_cron_observable)
