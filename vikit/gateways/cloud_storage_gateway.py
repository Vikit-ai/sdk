import os
from google.cloud import storage
from vikit.video.video import Video
import vikit.common.config as config

from loguru import logger


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
