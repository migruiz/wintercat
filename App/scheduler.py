import threading
import time
import reactivex as rx
import schedule


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


def cron_observable(execTime,outValue):

    booking = schedule.every().day.at(execTime)
   
    def observable(observer, _):
        def job():
            observer.on_next(outValue)

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

"""try:
    # Create the CRON Observable
    cron_stream = cron_observable()


    # Subscribe to the observable
    subscription = cron_stream.subscribe(
        on_next=lambda x: print(f"Received message: {x}"),
        on_error=lambda e: print(f"Error occurred: {e}"),
        on_completed=lambda: print("Stream completed!")
    )
    # Keep the program running to receive messages
    print("Press CTRL+C to exit...")

    while True:
        time.sleep(1)  # Keep the loop alive
except Exception:
    print("Caught an Exception, something went wrong...")
    time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    subscription.dispose()
    print("Subscription disposed and program terminated.")"""