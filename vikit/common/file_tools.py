import os
import re
import uuid as uuid
import urllib.parse
import sys

from typing import Union, Optional
from loguru import logger


def get_canonical_name(file_path: str):
    """
    Get the canonical name of a file, without the extension
    """
    return os.path.splitext(os.path.basename(file_path))[0]


def get_max_filename_length(path="."):
    """
    get the max file name for the current OS

    params:
        path: the file path

    return: file name max length.
    """
    try:
        return os.pathconf(path, "PC_NAME_MAX")
    except (AttributeError, ValueError, os.error):
        # PC_NAME_MAX may not be available or may fail for certain paths on some OSes
        # Returns a common default value (255) in this case
        return 255


def create_non_colliding_file_name(canonical_name: str = None, extension: str = "xyz"):
    """
    Transforms the filename to prevent collisions zith other files,
    by adding a UUID as suffix

    params:
        canonical_name: a name used as the target file name prefix
        extension: the extension of the file

    return: the non-colliding name
    """
    target_name = canonical_name + "_UID_" + str(uuid.uuid4()) + "." + extension

    val_target_name = get_path_type(target_name)
    if val_target_name["type"] == "error":
        logger.warning(
            f"Error creating non-colliding file name: {val_target_name['path']}"
        )

    logger.debug(f"val_target_name['path']: {val_target_name['path']}")
    return val_target_name["path"]


def get_safe_filename(filename):
    return re.sub(r"(?u)[^-\w.]", "", filename.strip().replace(" ", "_"))


def get_max_remote_path_length():
    """
    Get the maximum length of a remote path
    """
    return 2048


def is_valid_path(path: Optional[Union[str, os.PathLike]]) -> bool:
    """
    Check if the path is valid

    Args:
        path (str, os.PathLike): The path to validate

    Returns:
        bool: True if the path is valid, False otherwise
    """
    path = get_path_type(path)
    if path["type"] == "error" or path["type"] == "none":
        return False
    return True


def get_path_type(path: Optional[Union[str, os.PathLike]]) -> dict:
    """
    Validate the path and return its type

    Args:
        path (str, os.PathLike, ): The path to validate

    Returns:
        dict: The path type and the path itself
        Can be local, http, https, s3, gs, None, undefined, error,
    """
    logger.debug(f"Checking path: {path}")

    result = {"type": "undefined", "path": "undefined"}
    if path is None:
        return {"type": "none", "path": None}

    if len(path) > get_max_filename_length():
        return {
            "type": "error",
            "path": "The file name is too long for local filesystem storage",
        }

    if os.path.exists(path) or is_valid_filename(filename=os.path.basename(path)):
        logger.debug(f"Path is a PathLike object: {path}")
        return {"type": "local", "path": path}
    else:
        # Check if the path is a URL
        parsed_uri = urllib.parse.urlparse(str(path))

        if parsed_uri.scheme in ["http", "https", "s3", "gs"]:
            if len(parsed_uri.path) > get_max_remote_path_length():
                raise ValueError("The file name is too long for remote storage")
            return {"type": parsed_uri.scheme, "path": path}

    # by default, consider it as a local path
    return result


def is_valid_filename(filename: str) -> bool:
    """
    Check if the provided string is a valid filename for the local file system.

    Args:
        filename (str): The filename to check.

    Returns:
        bool: True if valid, False otherwise.
    """
    logger.debug(f"Checking filename: {filename}")
    # Check for invalid characters
    if sys.platform.startswith("win"):
        # Windows filename restrictions
        invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
        reserved_names = ["CON", "PRN", "AUX", "NUL"] + [
            f"{name}{i}" for name in ["COM", "LPT"] for i in range(1, 10)
        ]
        if any(filename.upper().startswith(reserved) for reserved in reserved_names):
            return False
    else:
        # Unix/Linux/MacOS filename restrictions
        invalid_chars = r"/"

    if re.search(invalid_chars, filename):
        return False

    # Check for leading or trailing spaces or dots which can be problematic
    if filename.strip(" .") != filename:
        return False

    # Check the length of the filename
    if len(filename) > get_max_filename_length():
        return False

    return True
