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

TESTS_MEDIA_FOLDER = "medias"
TRANSITION_BOY_IN_TRAIN = "transition_[seine]_from_Travel_to_travel.mp4"
TRANSITION_SEINE = "transition_[seine]_from_scene1_to_scene2.mp4"
SAMPLE_RECORDED_PROMPT_MEANINGLESS_LIFE = "upload.mp3"
SMALL_CAT_VIDEO_FILE_NAME = "chat_video_super8.mp4"
SMALL_VIDEOCRAFTER_VIDEO_FILE_NAME = "videocrafter.mp4"
SMALL_STABILITY_VIDEO_FILE_NAME = "stability.mp4"
SMALL_HAIPER_VIDEO_FILE_NAME = "haiper.mp4"
SMALL_RUNWAY_VIDEO_FILE_NAME = "runway.mp4"
INTERPOLATE_VIDEO_FILE_NAME = "interpolate.mp4"
GENERATED_3S_FOREST_VIDEO_SAMPLE_1 = "forest.mp4"
GENERATED_3S_FOREST_VIDEO_SAMPLE__2 = "treasures.mp4"
GENERATED_TRANSITION_FOREST_TREASURE_VIDEO_SAMPLE = (
    "transition_[seine]_from_treasures_to_forest.mp4"
)
PARIS_VIDEO = "Paris.mp4"
PARIS_SUBTITLE = "Paris_subtitles.srt"
TEST_PROMPT_RECORDING = "test.mp3"
TEST_PROMPT_RECORDING_TRAIN_BOY = "sub_audio_for_subtitle_from_0_to_13.mp3"
SAMPLE_GENERATED_MUSIC = "knowledgeStones_Forest_Symbols.mp3"
SAMPLE_GENERATED_BG_MUSIC = "PodcastSerenity.mp3"
SAMPLE_IMAGE_PROMPT = "image_prompt.jpeg"
SAMPLE_GCS_BUCKET = "dev-vikit-ai"
SAMPLE_GCS_OBJECT = "tests/file.txt"

_media_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), TESTS_MEDIA_FOLDER
)


def get_gcs_test_file_path():
    """
    Return the path to a file stored on Google Cloud Storage

    Here we assume the file is already present per convention at Vikit, though we might
    just as well create it on the fly (later version maybe)
    """
    return f"gs://{SAMPLE_GCS_BUCKET}/{SAMPLE_GCS_OBJECT}"


def get_gcs_test_object():
    """
    Return the path to a file stored on Google Cloud Storage
    """
    return SAMPLE_GCS_BUCKET, SAMPLE_GCS_OBJECT


def get_paris_subtitle_file():
    return os.path.join(_media_dir, PARIS_SUBTITLE)


def get_paris_video():
    return os.path.join(_media_dir, PARIS_VIDEO)


def get_interpolate_video():
    return os.path.join(_media_dir, INTERPOLATE_VIDEO_FILE_NAME)


def get_sample_gen_background_music():
    return os.path.join(_media_dir, SAMPLE_GENERATED_BG_MUSIC)


def get_cat_video_path():
    return os.path.join(_media_dir, SMALL_CAT_VIDEO_FILE_NAME)


def get_stabilityai_video_path():
    return os.path.join(_media_dir, SMALL_STABILITY_VIDEO_FILE_NAME)


def get_dynamicrafter_image_video_path(prompt):
    return os.path.join(_media_dir, SMALL_VIDEOCRAFTER_VIDEO_FILE_NAME)


def get_runway_image_video_path(prompt, aspect_ratio):
    return os.path.join(_media_dir, SMALL_RUNWAY_VIDEO_FILE_NAME)


def get_stabilityai_image_video_path():
    return os.path.join(_media_dir, SMALL_STABILITY_VIDEO_FILE_NAME)


def get_haiper_video_path():
    return os.path.join(_media_dir, SMALL_HAIPER_VIDEO_FILE_NAME)


def get_luma_video_path():
    return os.path.join(_media_dir, SMALL_LUMA_VIDEO_FILE_NAME)


def get_videocrafter_video_path():
    return os.path.join(_media_dir, SMALL_VIDEOCRAFTER_VIDEO_FILE_NAME)


def get_sample_generated_music_path():
    return os.path.join(_media_dir, SAMPLE_GENERATED_MUSIC)


def get_generated_3s_forest_video_1_path():
    """
    Return the path to the generated 3s forest video sample usually used as start
    """
    return os.path.join(_media_dir, GENERATED_3S_FOREST_VIDEO_SAMPLE_1)


def get_generated_3s_forest_video_2_path():
    """
    Return the path to the generated 3s forest video sample usually used as end
    """
    return os.path.join(_media_dir, GENERATED_3S_FOREST_VIDEO_SAMPLE__2)


def get_test_prompt_recording():
    """
    Return the path of a short prompt recording
    """
    return os.path.join(_media_dir, TEST_PROMPT_RECORDING)


def get_test_prompt_image():
    """
    Return the path of a image prompt input
    """
    return os.path.join(_media_dir, SAMPLE_IMAGE_PROMPT)


def get_test_prompt_recording_trainboy():
    """
    Return the path of a short prompt recording
    """
    return os.path.join(_media_dir, TEST_PROMPT_RECORDING_TRAIN_BOY)


def get_test_transition_stones_trainboy_path():
    return os.path.join(_media_dir, TRANSITION_BOY_IN_TRAIN)


def get_test_seine_transition_video_path():
    return os.path.join(_media_dir, TRANSITION_SEINE)


def get_test_recorded_prompt_path():
    return os.path.join(_media_dir, SAMPLE_RECORDED_PROMPT_MEANINGLESS_LIFE)
