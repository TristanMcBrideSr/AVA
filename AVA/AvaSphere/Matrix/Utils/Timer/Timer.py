import time
from functools import wraps

class Timer:
    LABEL_MAP = {
        None:  lambda label, elapsed, name: f"\n{name} took: {elapsed:.4f}s\n",
        "custom": lambda label, elapsed, name: f"\n[{label}] took: {elapsed:.4f}s\n"
    }

    @staticmethod
    def startAutomaticTimer(labelOrFunc=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start

                if isinstance(labelOrFunc, str) and labelOrFunc:
                    formatter = Timer.LABEL_MAP["custom"]
                    print(formatter(labelOrFunc, elapsed, func.__name__))
                else:
                    formatter = Timer.LABEL_MAP.get(labelOrFunc, Timer.LABEL_MAP[None])
                    print(formatter(labelOrFunc, elapsed, func.__name__))
                return result
            return wrapper

        return decorator(labelOrFunc) if callable(labelOrFunc) else decorator

    @staticmethod
    def startManualTimer():
        return time.time()

    @staticmethod
    def stopManualTimer():
        return time.time()

    @staticmethod
    def reportManualTimer(startTime, stopTime, label=None, name="Manual Timer"):
        elapsed = stopTime - startTime
        if label:
            formatter = Timer.LABEL_MAP["custom"]
            print(formatter(label, elapsed, name))
        else:
            formatter = Timer.LABEL_MAP.get(label, Timer.LABEL_MAP[None])
            print(formatter(label, elapsed, name))
        return elapsed
