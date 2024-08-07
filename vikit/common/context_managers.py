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
import random
import string
from datetime import datetime

from loguru import logger


class WorkingFolderContext:
    """
    This class is a context manager to change the working directory to the one specified
    in the constructor
    """

    def __init__(
        self, path=None, delete_on_exit=False, mark: str = None, include_mark=True
    ):
        """
        Allows for dynamic creation of a working folder, with the option to delete it on exit

        Args:
            path: the path to the working folder, if None a new folder will be created
            delete_on_exit: if True, the folder will be deleted on exit
            mark: a mark to help identify the working folder
        """
        logger.debug("Current Working Folder is: " + os.getcwd())
        if not mark:
            mark = inspect.stack()[1].function

        if path is None:
            now = datetime.now()
            date_string = now.strftime("%Y-%m-%d")

            temp_folder = os.path.join(
                "working_folder",
                date_string,
                "".join(random.choice(string.hexdigits) for i in range(20)),
            )
            if include_mark:
                temp_folder = temp_folder + ("-" + mark) if mark else temp_folder
            os.makedirs(temp_folder)
        else:
            if not os.path.exists(path):
                os.makedirs(path)
            temp_folder = path

        self.delete_on_exit = delete_on_exit
        self.path = temp_folder

    def __enter__(self):
        self.original_path = os.getcwd()
        os.chdir(self.path)
        logger.debug(f"Changed working directory to {self.path}")
        return self

    def __exit__(self, type, value, traceback):
        os.chdir(self.original_path)
        # We may uncomment this line to debug the program and see what has been generated
        if self.delete_on_exit:
            os.rmdir(self.path)
        if type is not None:  # An exception was raised
            logger.error(
                f"Exception handled, with details: {value} and trace {traceback}"
            )
        return False  # Propagate the exception.

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper
