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

from google.cloud import storage
from loguru import logger

import vikit.common.config as config
from vikit.video.video import Video


def upload_to_GCS_cloud_bucket(video: Video):
    """
    Upload file to Google Cloud Storage
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./gcpkey.json"
    # Instantiates a client
    storage_client = storage.Client()
    bucket = storage_client.bucket("aivideoscreated")
    blob = bucket.blob(video.unique_file_name)
    blob.upload_from_filename(video.source_file_path)
    final_video_path = f"{config.get_cloud_bucket_url()}/{video.unique_file_name}"
    logger.info(f"URL : {final_video_path}")

    return final_video_path
