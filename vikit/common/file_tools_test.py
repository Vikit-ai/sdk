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
"""
Test the file tools functions.

Includes tests of files required to be stored on public http url, non public
accessible cloud storage, and local files.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

import tests.testing_medias as testing_medias
from vikit.common.context_managers import WorkingFolderContext
from vikit.common.file_tools import (
    _parse_gcs_url,
    copy_file_from_gcs,
    download_or_copy_file,
    gcs_file_exists,
    get_public_uri_from_gcs_path,
    upload_to_bucket,
    url_exists,
)

BUCKET_NAME = "test-bucket"
SOURCE_FILE_NAME = "source-file.txt"
DESTINATION_FOLDER_NAME = "destination-folder"
DESTINATION_FILE_NAME = "destination-file.txt"


@pytest.mark.local_integration
@pytest.mark.asyncio
async def test_download_with_local_file():
    with WorkingFolderContext():
        local_file = testing_medias.get_cat_video_path()
        downloaded_file = await download_or_copy_file(local_file, "downloaded_cat.mp4")

        assert downloaded_file is not None
        assert downloaded_file == "downloaded_cat.mp4"
        assert downloaded_file != ""
        assert os.path.exists(downloaded_file)
        assert os.path.getsize(downloaded_file) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_download_or_copy_file__empty_url():
    """Test that download_or_copy_file raises ValueError with empty URL"""
    with pytest.raises(ValueError):
        _ = await download_or_copy_file(url="", local_path="downloaded_file.txt")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_download_or_copy_file__unexisting_path():
    """Test that download_or_copy_file raises ValueError with empty URL"""
    with pytest.raises(ValueError):
        _ = await download_or_copy_file(
            url="crazy://funny.com/a.jpg", local_path="downloaded_file.txt"
        )


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [testing_medias.GCS_TEST_FILE_GS_URL, testing_medias.GCS_TEST_FILE_HTTPS_URL],
)
async def test_download_from_google_cloud_storage(url):
    """
    Test the download of a file stored on a Google cloud storage bucket.

    Prerequisites:
        Will need an access token to Google Cloud Storage,
            - either you use gcloud auth application-default login and connect with
            your identity before running the tests
            - or you ensure a service account key file with low privileges (i.e. just
            read the test bucket files) is available
            - You could also call the secret manager to get the SA key from it using
            your own credentials (better for traceability but overkill here)
    """
    with WorkingFolderContext():
        downloaded_file = await download_or_copy_file(url, "downloaded_file.abc")

        assert downloaded_file is not None
        assert downloaded_file == "downloaded_file.abc"
        assert downloaded_file != ""
        assert os.path.exists(downloaded_file)


@pytest.mark.unit
def test_copy_file_from_gcs_invalid_url():
    """Test that copy_file_from_gcs raises ValueError with empty URL"""
    with pytest.raises(ValueError):
        copy_file_from_gcs(blob_path="", bucket="", destination_file_name="")


@pytest.mark.integration
def test_copy_file_from_gcs():
    """Test copying file from GCS"""
    gcs_bucket, gcs_object = testing_medias.get_gcs_test_object()
    with WorkingFolderContext():
        result = copy_file_from_gcs(
            gcs_bucket,
            gcs_object,
            destination_file_name="test_download.txt",
        )
        assert result == "test_download.txt"
        assert os.path.exists("test_download.txt")


@pytest.mark.integration
def test_gcs_file_exists__success():
    gcs_bucket, gcs_object = testing_medias.get_gcs_test_object()
    with WorkingFolderContext():
        result = gcs_file_exists(gcs_bucket, gcs_object)
        assert result is True


@pytest.mark.integration
def test_gcs_file_exists__failure():
    gcs_bucket, gcs_object = testing_medias.get_gcs_test_object()
    with WorkingFolderContext():
        result = gcs_file_exists(gcs_bucket, "non_existent_file.txt")
        assert result is False


@pytest.mark.integration
def test_gcs_file_exists__invalid_bucket():
    gcs_bucket, gcs_object = testing_medias.get_gcs_test_object()
    with WorkingFolderContext():
        result = gcs_file_exists("invalid_bucket", gcs_object)
        assert result is False


@pytest.mark.integration
def test_url_exists__success():
    gcs_bucket, gcs_object = testing_medias.get_gcs_test_object()
    with WorkingFolderContext():
        result = url_exists("gs://{}/{}".format(gcs_bucket, gcs_object))
        assert result is True


@pytest.mark.integration
def test_gcs_file_exists__invalid_object():
    """Test the gcs_file_exists function"""
    gcs_bucket, gcs_object = testing_medias.get_gcs_test_object()
    with WorkingFolderContext():
        result = gcs_file_exists(gcs_bucket, "invalid_object")
        assert result is False


@pytest.mark.unit
@pytest.mark.parametrize(
    "url, expected_result",
    [
        # Normal URLs
        (
            "http://storage.googleapis.com/bucket/path/to/file",
            (True, "bucket", "path/to/file"),
        ),
        (
            "https://storage.cloud.google.com/bucket/path/to/file",
            (True, "bucket", "path/to/file"),
        ),
        (
            "https://storage.googleapis.com/bucket/path/to/file",
            (True, "bucket", "path/to/file"),
        ),
        (
            "gs://bucket/path/to/file",
            (True, "bucket", "path/to/file"),
        ),
        # URLs with encoded characters
        (
            "https://storage.googleapis.com/bucket/urlencoded%20path",
            (True, "bucket", "urlencoded path"),
        ),
        # Valid edge cases
        ("https://storage.googleapis.com", (True, "", "")),
        ("https://storage.googleapis.com/", (True, "", "")),
        ("https://storage.googleapis.com/bucket", (True, "bucket", "")),
        ("https://storage.googleapis.com/bucket/", (True, "bucket", "")),
        # Invalid GCS URLs
        ("unsupported_protocol://bucket/object", (False, None, None)),
        ("https://not-gcs.com/bucket/object", (False, None, None)),
    ],
)
def test_parse_gcs_url(url, expected_result):
    result = _parse_gcs_url(url)
    assert result == expected_result, f"Expected {expected_result}, but got {result}"


@patch("google.cloud.storage.Client")
@pytest.mark.unit
async def test_upload_to_bucket(mock_storage_client):
    mock_bucket = MagicMock()
    mock_bucket.name = BUCKET_NAME

    mock_blob = MagicMock()
    mock_blob.name = os.path.join(DESTINATION_FOLDER_NAME, DESTINATION_FILE_NAME)

    mock_storage_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    result = await upload_to_bucket(
        SOURCE_FILE_NAME,
        DESTINATION_FOLDER_NAME,
        DESTINATION_FILE_NAME,
        bucket_name=BUCKET_NAME,
    )

    mock_storage_client.return_value.bucket.assert_called_once_with(BUCKET_NAME)
    mock_bucket.blob.assert_called_once_with(
        os.path.join(DESTINATION_FOLDER_NAME, DESTINATION_FILE_NAME)
    )
    mock_blob.upload_from_filename.assert_called_once_with(SOURCE_FILE_NAME, timeout=60)

    expected_result = (
        f"gs://{BUCKET_NAME}/{DESTINATION_FOLDER_NAME}/{DESTINATION_FILE_NAME}"
    )
    assert result == expected_result, f"expected: {expected_result} but was: {result}"


@pytest.mark.parametrize(
    "source_file_name, destination_folder_name, destination_file_name",
    [
        ("", "dst-folder", "dst-file.txt"),
        ("src-file.txt", "", ""),
        ("", "", ""),
        (None, "dst-folder", "dst-file.txt"),
        ("src-file.txt", None, None),
        (None, None, None),
    ],
)
@pytest.mark.unit
async def test_upload_to_bucket_invalid_parameters(
    source_file_name, destination_folder_name, destination_file_name
):
    with pytest.raises(ValueError):
        await upload_to_bucket(
            source_file_name,
            destination_folder_name,
            destination_file_name,
            bucket_name="test-bucket",
        )


@pytest.mark.parametrize(
    "gcs_path, expected_public_uri",
    [
        (
            "gs://bucket-name/folder/file.txt",
            "https://storage.googleapis.com/bucket-name/folder/file.txt",
        ),
        (
            "gs://another-bucket/some/other/file.txt",
            "https://storage.googleapis.com/another-bucket/some/other/file.txt",
        ),
        ("gs://bucket-name/", "https://storage.googleapis.com/bucket-name/"),
    ],
)
@pytest.mark.unit
def test_get_public_uri_from_gcs_path(gcs_path, expected_public_uri):
    result = get_public_uri_from_gcs_path(gcs_path)
    assert result == expected_public_uri, (
        f"Expected {expected_public_uri}, but got {result}"
    )
