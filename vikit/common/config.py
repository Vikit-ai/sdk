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
from os import path

from dotenv import load_dotenv
from loguru import logger

import uuid

# Get the absolute path to the directory this file is in.
# TODO: make this cleaner and more robust by using the __file__ attribute
dir_path = path.dirname(path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_file = os.path.join(
    dir_path, ".env.config." + os.getenv("CONFIG_ENVIRONMENT", "dev")
)
if not os.path.exists(env_file):
    logger.warning(f"config file {env_file} does not exist")
else:
    load_dotenv(dotenv_path=env_file)

creation_uuid = str(uuid.uuid4())


def get_media_polling_interval() -> int:
    media_polling_interval = os.getenv("MEDIA_POLLING_INTERVAL", 10)
    if media_polling_interval is None:
        raise Exception("MEDIA_POLLING_INTERVAL is not set")
    return int(media_polling_interval)


def get_default_background_music() -> str:
    default_background_music = os.getenv("DEFAULT_BACKGROUND_MUSIC", None)
    if default_background_music is None:
        raise Exception("DEFAULT_BACKGROUND_MUSIC is not set")
    bg_music_path = os.path.join(dir_path, default_background_music)
    logger.debug(f"Default background music: {bg_music_path}")
    return bg_music_path


def get_elevenLabs_url() -> str:
    elevenLabs_url = os.getenv("ELEVEN_LABS_API_URI", None)
    if elevenLabs_url is None:
        raise Exception("ELEVEN_LABS_API_URI is not set")
    return elevenLabs_url


def get_vikit_backend_url() -> str:
    vikitBackend_url = os.getenv("VIKIT_BACKEND_URI", None)
    if vikitBackend_url is None:
        return "https://videho.replit.app/models"
    return vikitBackend_url


def get_videho_email_contact() -> str:
    videho_email = os.getenv("VIDEHO_EMAIL_CONTACT", None)
    if videho_email is None:
        raise Exception("VIDEHO_EMAIL_CONTACT is not set")
    return videho_email


def get_nb_retries_http_calls() -> int:
    nb_retries_http_calls = os.getenv("NB_RETRIES_HTTP_CALLS", 3)
    if nb_retries_http_calls is None:
        raise Exception("NB_RETRIES_HTTP_CALLS is not set")
    return int(nb_retries_http_calls)


def get_prompt_mp3_file_name(uuid=creation_uuid) -> str:
    """
    The name of the mp3 file either converted from user  or
    generated using an llm and that we use to extract subtitles from the video
    """
    prompt_mp3_file_name = os.getenv(
        "PROMPT_MP3_FILE_NAME", "prompt_upload_" + uuid + ".mp3"
    )
    if prompt_mp3_file_name is None:
        raise Exception("PROMPT_MP3_FILE_NAME is not set")
    return prompt_mp3_file_name


def get_subtitles_min_duration() -> int:
    subtitles_min_duration = os.getenv("SUBTITLES_MIN_DURATION", 7)
    if subtitles_min_duration is None:
        raise Exception("SUBTITLES_MIN_DURATION is not set")
    return int(subtitles_min_duration)


def get_video_length_per_subtitle() -> int:
    """
    The length of the video generated for each subtitle is currently directly
    linked to the maximum amount of time allowed by videocrafter
    """
    video_length_per_subtitle = os.getenv("STEPS", 300)
    if video_length_per_subtitle is None:
        raise Exception("STEPS is not set")
    return int(video_length_per_subtitle)


def get_nb_subs_per_video() -> int:
    """
    The number of subtitles to generate per video
    """
    nb_subs_per_video = os.getenv("NUMBER_OF_SUBTITLES_PER_VIDEO_PROMPT", 1)
    if nb_subs_per_video is None:
        raise Exception("NUMBER_OF_SUBTITLES_PER_VIDEO_PROMPT is not set")
    return int(nb_subs_per_video)


def get_subtitles_default_file_name(uuid=creation_uuid) -> str:
    """
    The default name used to save the subtitles file in the working directory
    It is typically build from smaller subtitles generated for subvideos
    """
    subtitles_default_file_name = os.getenv(
        "SUBTITLES_FILE_NAME", "subtitles_" + uuid + ".srt"
    )
    if subtitles_default_file_name is None:
        raise Exception("SUBTITLES_FILE_NAME is not set")
    return subtitles_default_file_name


def get_cleanup_tempfiles() -> bool:
    """
    Whether to cleanup temporary files or not. By default we set it to False
    as we prefer to keep the files for debugging purposes or to train future models,
    or even reuse the produced sub videos
    """
    cleanup_tempfiles = os.getenv("CLEANUP_TEMPFILES", False)
    if cleanup_tempfiles is None:
        raise Exception("CLEANUP_TEMPFILES is not set")
    return bool(cleanup_tempfiles)


def get_test_mode() -> bool:
    """
    Are we using the real Vikit Gateway or a fake one for local_integration tests
    """
    test_mode = os.getenv("TEST_MODE", False)
    if test_mode is None:
        raise Exception("TEST_MODE is not set")
    return bool(test_mode)


def get_sub_audio_for_subtitle_prefix():
    """
    The prefix for the file name of the audio file that will be used for the subtitles video
    """
    sub_audio_for_subtitle_prefix = os.getenv(
        "SUB_AUDIO_FOR_SOUND_PREFIX", "sub_audio_for_sound_" + creation_uuid
    )
    if sub_audio_for_subtitle_prefix is None:
        raise Exception("SUB_AUDIO_FOR_SOUND_PREFIX is not set")
    return sub_audio_for_subtitle_prefix


def get_initial_audio_file_name():
    """
    The file name of the user provided or llm generated audio file
    """
    initial_audio_file_name = os.getenv(
        "INITIAL_AUDIO_FILE_NAME", "upload_" + creation_uuid + ".mp3"
    )
    if initial_audio_file_name is None:
        raise Exception("INITIAL_AUDIO_FILE_NAME is not set")
    return initial_audio_file_name


def get_video_list_file_name(uuid=creation_uuid):
    """
    The file name of the list of videos files to mix with ffmpeg
    """
    video_list_file_name = os.getenv(
        "VIDEO_LIST_FILE_NAME", "videosToMerge" + uuid + ".txt"
    )
    if video_list_file_name is None:
        raise Exception("VIDEO_LIST_FILE_NAME is not set")
    return video_list_file_name


def get_max_file_size_url_gemini() -> int:
    max_file_size_url_gemini = os.getenv("MAX_FILE_SIZE_URL_GEMINI", 6500000)
    if max_file_size_url_gemini is None:
        raise Exception("MAX_FILE_SIZE_URL_GEMINI is not set")
    return int(max_file_size_url_gemini)
