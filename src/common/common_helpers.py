import time


def time_measurement_decorator(timer_name: str):
    def wrapper(func):
        def inner(*args, **kwargs):
            start_time: float = time.time()
            result = func(*args, **kwargs)
            end_time: float = time.time()
            elapsed_time: float = end_time - start_time
            print(f"{timer_name} time: {elapsed_time*1000:.6f} ms")
            return result
        return inner
    return wrapper
