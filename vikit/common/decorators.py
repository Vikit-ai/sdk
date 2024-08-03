# Copyright 2024 Vikit.ai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import inspect
import os
import time
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
        )[:50]

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
