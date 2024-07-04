import os
import re
import uuid as uuid
import urllib.parse

from typing import Union, Optional


def get_canonical_name(file_path: str):
    """
    Get the canonical name of a file, without the extension
    """
    return os.path.splitext(os.path.basename(file_path))[0]


def get_max_filename_length(path="."):
    """
    Fit the file name to a certain length, by removing the last characters if it is too long

    params:
    file_name: the file name to be fitted

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
    val_target_name = get_validated_path(target_name)

    return val_target_name["path"]


def get_safe_filename(filename):
    return re.sub(r"(?u)[^-\w.]", "", filename.strip().replace(" ", "_"))


def get_max_remote_path_length():
    """
    Get the maximum length of a remote path
    """
    return 2048


def get_validated_path(path: Optional[Union[str, os.PathLike]]) -> dict:
    """
    Validate the path and return its type

    Args:
        path (str, os.PathLike): The path to validate

    Returns:
        dict: The path type and the path itself
    """
    if path is None:
        return {"type": "none", "path": None}

    if isinstance(path, os.PathLike) or os.path.isabs(path):
        if len(path) > get_max_filename_length():
            raise ValueError("The file name is too long for local filesystem storage")
        return {"type": "local", "path": path}

    # Check if the path is a URL
    parsed_uri = urllib.parse.urlparse(str(path))
    if parsed_uri.scheme in ["http", "https", "s3", "gs"]:
        if len(parsed_uri.path) > get_max_remote_path_length():
            raise ValueError("The file name is too long for remote storage")
        if "stream" in parsed_uri.path:
            return {"type": "streaming", "path": path}
        else:
            return {"type": "cloud", "path": path}

    # by default, consider it as a local path
    return {"type": "local", "path": path}
