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

import os
import re
import shutil
import sys
import urllib.parse
from typing import Optional, Union
from urllib.parse import quote

import aiofiles
import aiohttp
import requests

# Maybe we will consider breaking down the copying logic into modules to prevent adding too many dependencies on external linbs
from google.cloud import storage
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from vikit.common.config import (
    get_gcs_upload_timeout_sec,
    get_nb_retries_http_calls,
)

TIMEOUT = 10  # seconds before stopping the request to check an URL exists


def get_canonical_name(file_path: str):
    """
    Get the canonical name of a file, without the extension
    """
    return os.path.splitext(os.path.basename(file_path))[0]


def get_max_path_length(path="."):
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


def _parse_gcs_url(url: str) -> tuple[bool, str, str]:
    """
    Converts a Google Cloud Storage HTTP(S) URL to a bucket and blob path.

    GCS URLs have the form: http(s)://storage.googleapis.com/bucket/blob_path when publicly accessible
    or http(s)://storage.cloud.google.com/bucket/blob_path when private.

    GCS URLs can also be in the gs:// format, in which case the netloc becomes the bucket name.

    Returns:
        bool: True if the URL is a GCS URL, False otherwise.
        str: The bucket name, or None if the URL is not a GCS URL.
        str: The blob path, or None if the URL is not a GCS URL.
    """
    parsed_url = urllib.parse.urlparse(url)
    logger.debug(f"parsed_url: {parsed_url}")
    if parsed_url.scheme not in ["http", "https", "gs"]:
        return False, None, None
    if parsed_url.scheme in ["http", "https"]:
        if parsed_url.netloc not in [
            "storage.googleapis.com",
            "storage.cloud.google.com",
        ]:
            return False, None, None
        else:
            parts = parsed_url.path.split("/")
            if len(parts) >= 2:
                _, bucket, *path_segments = parts
            else:
                bucket = parts[0] if parts else ""
                path_segments = []
            path = "/".join(path_segments)
        if not parsed_url.path:
            return True, "", ""
        path = urllib.parse.unquote("/".join(path_segments))
    else:
        bucket = parsed_url.netloc
        path = parsed_url.path[1:]

    return True, bucket, path


def get_safe_filename(filename):
    return re.sub(r"(?u)[^-\w.]", "", filename.strip().replace(" ", "_"))


def get_max_remote_path_length():
    """
    Get the maximum length of a remote path
    """
    return 2048


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
    if len(filename) > get_max_path_length():
        return False

    return True


def web_url_exists(url):
    try:
        logger.debug(f"Checking web_url_exists for URL: {url}")
        response = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False


def file_url_exists(url):
    """
    Check if a file URL exists locally
    """
    logger.debug(f"Checking file URL: {url}")
    if url.startswith("file://"):
        file_path = url[7:]  # Remove 'file://' prefix
        return os.path.exists(file_path)
    return False


def url_exists(url: str):
    """
    Check if a URL exists somewhere on the internet or locally. To be superseded by a more
    versatile and unified library in the future.

    Args:
        url (str): The URL to check

    Returns:
        bool: True if the URL exists, False otherwise
    """
    does_url_exists = False
    assert url, "url cannot be None"

    if os.path.exists(url):
        does_url_exists = True

    if file_url_exists(url):
        does_url_exists = True

    if web_url_exists(url):
        does_url_exists = True

    is_gcs_url, bucket, file_path = _parse_gcs_url(url)
    logger.debug(f"is_gcs_url, bucket, file_path: {is_gcs_url}, {bucket}, {file_path}")
    if is_gcs_url:
        does_url_exists = gcs_file_exists(
            bucket=bucket,
            file_path=file_path,
        )

    return does_url_exists


def gcs_file_exists(bucket: str, file_path: str) -> bool:
    does_url_exists = False
    try:
        storage_client = storage.Client()
        gcs_bucket = storage_client.bucket(bucket)
        blob = gcs_bucket.blob(file_path)
        logger.debug(
            f"Checking GCS URL on blob: {blob} , does it exist?: {blob.exists()}"
        )
        does_url_exists = blob.exists()
    except Exception as e:
        logger.error(f"Error checking GCS URL: {e}")
        does_url_exists = False
    return does_url_exists


def is_valid_path(path: Optional[Union[str, os.PathLike]]) -> bool:
    """
    Check if the path is valid: could be a local path or a remote one
    (http, etc). We don't test the actual access and credentials at this stage,
    just the path format.

    Args:
        path (str, os.PathLike): The path to validate

    Returns:
        bool: True if the path is valid, False otherwise
    """
    path, error = get_path_type(path)
    if error:
        return False
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
        Path type can be local, http, https, s3, gs, None, undefined, error,
        error : message if the path is invalid, None if no error
    """
    logger.debug(f"Checking path: {path}")
    result = {"type": "undefined", "path": "undefined"}, "undefined path"

    if path is None:
        return {"type": "none", "path": path}, "The path is None"

    # Check if the path is a URL
    parsed_uri = urllib.parse.urlparse(str(path))
    if parsed_uri.scheme in ["http", "https", "gs"]:
        return {"type": parsed_uri.scheme, "path": path}, None

    if path.startswith("file://"):
        logger.debug(f"Path is a local url format: {path}")
        if len(path) > get_max_path_length():
            return {
                "type": "error",
                "path": "",
            }, "The file name is too long for local filesystem storage"

        return {"type": "local_url_format", "path": path}, None
    if os.path.isdir(path) or os.path.isfile(path):
        if len(path) > get_max_path_length():
            return {
                "type": "error",
                "path": "",
            }, "The file name is too long for local filesystem storage"

        return {"type": "local", "path": path}, None

    # by default, consider it as a local path
    return result


@retry(
    stop=stop_after_attempt(get_nb_retries_http_calls()),
    wait=wait_exponential(min=4, max=10),
    reraise=True,
)
async def download_or_copy_file(
    url: str,
    local_path: str,
    force_download: bool = False,
    enable_gcs_url_rewrite: bool = True,
) -> str:
    """
    Download a file from a URL to a local file asynchronously

    Args:
        url (str): The URL to download the file from (supported: http, https, gs, local)
        local_path (str): The filename to save the file to.
        force_download (bool): If True, the file will be downloaded even if it already
            exists
        enable_gcs_url_rewrite (bool): If True, the GCS Cloud Storage libraries will be
            used for HTTP(S) URLs pointing to cloud storage resource. If False, the file
            will be downloaded using the HTTP(S) protocol. This parameter exists mainly
            for testing purposes. We recommend using the GCS library whenever possible.

    Returns:
        str: The filename of the downloaded file.
    """
    if not url:
        raise ValueError("URL must be provided")

    # Replace the Google Cloud Storage URL with the gs:// format in order to take
    # advantage of the google.cloud.storage library as much as possible.
    is_gcs_url, bucket, file_path = _parse_gcs_url(url)
    if is_gcs_url and enable_gcs_url_rewrite:
        gs_url = f"gs://{bucket}/{file_path}"
        logger.debug(f"Replacing HTTP(S) URL with GCS URL:\nold: {url}\nnew: {gs_url}")
        url = gs_url

    path_desc, error = get_path_type(url)
    if error:
        raise ValueError(f"Unsupported remote path type: {url} with error: {error}")

    if len(local_path) > 255:
        truncated_path = local_path[-255:]
        logger.warning(
            "Local path is too long, truncating:"
            f"\nold: {local_path}\nnew: {truncated_path}"
        )
        local_path = truncated_path
    if os.path.exists(local_path) and not force_download:
        logger.debug(f"File already exists at {local_path}, skipping download")
        return local_path

    if path_desc["type"] == "http" or path_desc["type"] == "https":
        async with aiohttp.ClientSession() as session:
            logger.debug(f"Downloading file from {url} to {local_path}")
            async with session.get(url) as response:
                _check_http_response(response)

                # Use aiofiles to write the content asynchronously.
                async with aiofiles.open(local_path, "wb") as f:
                    # Read the content in chunks of 1MB to avoid using a lot of memory.
                    async for chunk in response.content.iter_chunked(1024 * 1024):
                        await f.write(chunk)
                return local_path

    elif path_desc["type"] == "local":
        logger.debug(f"Copying file from {url} to {local_path}")
        if url == local_path:
            logger.debug(f"File already exists at {local_path}, skipping copy")
            return local_path
        else:
            shutil.copyfile(url, local_path)
        return local_path
    elif path_desc["type"] == "local_url_format":
        url = url.replace("file://", "")
        logger.debug(f"Copying file from {url} to {local_path}")
        shutil.copyfile(url, local_path)
        return local_path
    elif path_desc["type"] == "gs":
        return copy_file_from_gcs(
            bucket=url.split("/")[2],
            blob_path="/".join(url.split("/")[3:]),
            destination_file_name=local_path,
        )
    else:
        raise ValueError(f"Unsupported path type: {path_desc['type']} for url: {url}")


def _check_http_response(response: aiohttp.ClientResponse):
    """Throws the appropriate exception if the response indicates an error."""
    if response.status == 200:
        return

    if response.status == 403:
        raise PermissionError(response)
    if response.status == 404:
        raise FileNotFoundError(response)

    # TODO: Add more specialized errors here. See the full list of available errors at
    # https://docs.python.org/3/library/exceptions.html

    raise ConnectionError(response)


def copy_file_from_gcs(
    bucket: str, blob_path: str, destination_file_name: str = "downloaded_file"
):
    """
    Copy a file from Google Cloud storage using the API

    params:
        gcs_full_url: the full URL of the file to copy
        blob_path: the name of the object to copy
        destination_file_name: the local path of the copied file

    return: the local path of the copied file

    """
    if not bucket or not object:
        raise ValueError("No GCS bucket or object provided")
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(blob_path)
    blob.download_to_filename(destination_file_name)

    logger.debug(f"Blob {blob_path} downloaded to {destination_file_name}.")

    return destination_file_name


async def upload_to_bucket(
    source_file_name,
    destination_blob,
    destination_file_name,
    bucket_name,
):
    if not source_file_name:
        raise ValueError("source_file_name cannot be None or empty string")
    if not destination_blob:
        raise ValueError("destination_blob cannot be None or empty string")
    if not destination_file_name:
        raise ValueError("destination_file_name cannot be None or empty string")
    if not bucket_name:
        raise ValueError("bucket_name cannot be None or empty string")

    bucket = storage.Client().bucket(bucket_name)
    blob = bucket.blob(f"{destination_blob}/{destination_file_name}")
    blob.upload_from_filename(source_file_name, timeout=get_gcs_upload_timeout_sec())

    gcs_url = f"gs://{bucket.name}/{blob.name}"
    logger.debug(f"Uploaded {source_file_name} to {gcs_url}, Blob name is {blob.name}")

    return gcs_url


# TODO: get the public URI from GCS path


def get_public_uri_from_gcs_path(gcs_path: str) -> str:
    inferred_public_path = f"https://storage.googleapis.com/{gcs_path.lstrip('gs://')}"
    inferred_public_path = quote(inferred_public_path, safe=":/")

    logger.debug(
        f"Inferred public path: {inferred_public_path} from GCS path: {gcs_path}"
    )
    return inferred_public_path
