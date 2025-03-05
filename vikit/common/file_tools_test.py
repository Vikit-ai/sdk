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

import pytest

import tests.testing_medias as testing_medias
from vikit.common.context_managers import WorkingFolderContext
from vikit.common.file_tools import (
    _parse_gcs_url,
    copy_file_from_gcs,
    download_or_copy_file,
)


class TestFileTools:
    """
    Test the file tools functions

    Includes tests of files required to be stored on public http url, non public accessible cloud storage, and local files
    """

    @pytest.mark.local_integration
    @pytest.mark.asyncio
    async def test_Download_with_local_file(self):
        """
        Test the download of a local file
        """
        with WorkingFolderContext():
            local_file = testing_medias.get_cat_video_path()
            downloaded_file = await download_or_copy_file(
                local_file, "downloaded_cat.mp4"
            )

            assert downloaded_file is not None
            assert downloaded_file == "downloaded_cat.mp4"
            assert downloaded_file != ""
            assert os.path.exists(downloaded_file)
            assert os.path.getsize(downloaded_file) > 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "url",
        [testing_medias.GCS_TEST_FILE_GS_URL, testing_medias.GCS_TEST_FILE_HTTPS_URL],
    )
    async def test_Download_from_google_cloud_storage(self, url):
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

    @pytest.mark.integration
    def test_copy_file_from_gcs_invalid_url(self):
        """Test that copy_file_from_gcs raises ValueError with empty URL"""
        with pytest.raises(ValueError):
            copy_file_from_gcs(blob_path="", bucket="", destination_file_name="")

    @pytest.mark.integration
    def test_copy_file_from_gcs(self):
        """Test copying file from GCS"""
        gcs_bucket, gcs_object = testing_medias.get_gcs_test_object()
        with WorkingFolderContext():
            result = copy_file_from_gcs(
                gcs_bucket, gcs_object, destination_file_name="test_download.txt"
            )
            assert result == "test_download.txt"
            assert os.path.exists("test_download.txt")

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
                "https://storage.googleapis.com/bucket/path/to/file",
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
    def test_parse_gcs_url(self, url, expected_result):
        result = _parse_gcs_url(url)
        assert result == expected_result, result
