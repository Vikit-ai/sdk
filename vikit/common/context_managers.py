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

from vikit.common.config import get_default_working_folder_root


class WorkingFolderContext:
    """
    This class is a context manager to change the working directory to the one specified
    by the constructor parameters.

    WARNING: Not thread safe. This class it is meant to be used in a synchronous context
    or by launching several ones in separate processes as we change directory in the
    process.
    """

    def __init__(
        self,
        root=None,
        mark: str = "mark",
        include_mark=True,
        include_caller_stack=False,
        insert_date=True,
        insert_minutes=True,
        date_format="%Y-%m-%d",
        insert_small_id=True,
    ):
        """
        Allows for dynamic creation of a working folder.

        Args:
            root: The root directory for the working folder path. If None, a default
                root directory will be used.
            mark: A string identifier to help distinguish the working folder.
            include_mark: If True, the `mark` will be included in the folder path.
            include_caller_stack: If True, the caller's function name will be included in
                the folder path.
            insert_date: If True, the current date will be included in the folder path.
            insert_minutes: If True, the current time (hours and minutes) will be included
                in the folder path.
            date_format: The format of the date to include in the folder path.
            insert_small_id: If True, a randomly generated 10-character alphanumeric ID
                will be included in the folder path.
        """
        logger.debug("Current Working Folder is: " + os.getcwd())

        if include_caller_stack:
            mark = inspect.stack()[1].function

        if include_mark and not mark:
            raise ValueError("If include_mark is set, mark must be set also.")

        now = datetime.now()
        date_string = now.strftime(date_format)
        self.small_id = "".join(random.choice(string.hexdigits) for i in range(10))
        temp_folder = ""

        self.delivery_folder_suffix = ""
        self.delivery_folder_suffix += date_string + os.sep if insert_date else ""
        self.delivery_folder_suffix += (
            now.strftime("%H-%M") + os.sep if insert_minutes else ""
        )
        self.delivery_folder_suffix += mark + os.sep if include_mark else ""
        self.delivery_folder_suffix += self.small_id + os.sep if insert_small_id else ""
        self.delivery_folder_suffix = self.delivery_folder_suffix.rstrip("/")

        if not root:
            root = get_default_working_folder_root()

        new_path = os.path.join(root, self.delivery_folder_suffix)
        logger.debug(
            f"Creating new path: {new_path}, root is {root}, suffix is "
            f"{self.delivery_folder_suffix}"
        )

        os.makedirs(new_path, exist_ok=True)
        temp_folder = os.path.join(os.path.abspath(os.getcwd()), new_path)
        logger.debug(f"Context Manager - Created new folder: {temp_folder}")

        self.path = temp_folder

    def __enter__(self):
        self.original_path = os.getcwd()
        os.chdir(self.path)
        logger.debug(f"Changed working directory to {self.path}")
        return self

    def __exit__(self, wrapped_type, value, traceback):
        os.chdir(self.original_path)
        if wrapped_type is not None:  # An exception was raised
            logger.error(
                f"Exception handled, with details: {value} and trace {traceback}"
            )
        return False  # Propagate the exception.

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper

    def get_delivery_folder_suffix(self) -> str:
        """
        Get a unique delivery folder.

        Returns:
            A unique folder name without the root folder path. For example, if the
            full path is `/root_folder/2024-01-01-12-00-1234567890-MyMark`, this method
            will return `2024-01-01-12-00-1234567890-MyMark`.
        """
        return self.delivery_folder_suffix
