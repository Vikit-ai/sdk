import time
import inspect
import os

from functools import wraps
from loguru import logger


def log_function_params(func):
    """
    Decorator to log the parameters of a function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper function to log the parameters of a function

        """
        start_time = time.time()
        param_values = (
            ", ".join(repr(arg) for arg in args)
            + ", "
            + ", ".join(f"{key}={value}" for key, value in kwargs.items())
        )

        # Get the name of the test from the call stack
        stack = inspect.stack()
        test_name = None
        for frame in stack:
            if frame.function.startswith("test_"):
                test_name = frame.function
                break

        logger.debug(
            f"Called function {func.__name__} with parameters : {param_values} in module {func.__module__} from test {test_name}, current folder is {os.getcwd()}"
        )
        result = func(*args, **kwargs)
        logger.debug(
            f"Returned from {func.__name__} : {result} in module {func.__module__} from test {test_name}"
        )
        end_time = time.time()
        logger.debug(
            f"Execution time for {func.__name__} : {end_time - start_time} on in module {func.__module__} from test {test_name}"
        )

        return result

    return wrapper


def delay(seconds):
    """
    Decorator to delay the execution of a function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            if type(seconds) is int and seconds > 0:  # fail open
                time.sleep(seconds)
                return func(*args, **kwargs)

        return wrapper

    return decorator
