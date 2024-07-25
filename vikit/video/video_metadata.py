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

import uuid


class VideoMetadata:
    """
    Hybrid DTO class for storing video metadata.

    Attributes:
    title (str): Title of the video.
    duration (int): Duration of the video in seconds.
    height (str): height of the video.
    width (str): width of the video.
    is_video_generated (bool): Whether the video is generated.
    is_reencoded (bool): Whether the video is reencoded.
    is_interpolated (bool): Whether the video is interpolated.
    is_bg_music_applied (bool): Whether the background music is applied.
    is_bg_music_generated (bool): Whether the background music is generated.
    is_subtitle_audio_applied (bool): Whether the subtitle audio is applied, useful for music tracks
    is_prompt_read_aloud (bool): Whether the prompt text is read aloud by synthetic voice.

    extra_metadata (dict): Extra metadata for the video.
    """

    def __init__(
        self,
        id: uuid = None,
        title=None,
        duration=None,
        width: int = None,
        height: int = None,
        top_parent_id=None,
        is_video_generated=False,
        is_reencoded=False,
        is_interpolated=False,
        is_bg_music_applied=False,
        is_subtitle_audio_applied=False,
        is_bg_music_generated=None,
        is_prompt_read_aloud=False,
        **custom_metadata,
    ):
        self.id = id
        self.title = title
        self.duration = duration
        self.width = width
        self.height = height
        self.is_video_generated = is_video_generated
        self.is_reencoded = is_reencoded
        self.is_interpolated = is_interpolated
        self.bg_music_applied = is_bg_music_applied
        self.is_subtitle_audio_applied = is_subtitle_audio_applied
        self.is_bg_music_generated = is_bg_music_generated  # if not using gnerated we infer the default bg music is used
        self.top_parent_id = top_parent_id
        self.is_prompt_read_aloud = is_prompt_read_aloud

        self.custom_metadata = custom_metadata

    def __str__(self):
        return f"VideoMetadata(title={self.title}, duration={self.duration}, width={self.width}, height={self.height}, is_video_generated={self.is_video_generated}, is_reencoded={self.is_reencoded}, is_interpolated={self.is_interpolated}, bg_music_applied={self.bg_music_applied}, is_bg_music_generated={self.is_bg_music_generated}, extra_metadata={self.extra_metadata})"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            return self.custom_metadata[key]

    def __setitem__(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)  # update the attribute
        else:
            self.custom_metadata[key] = value

    def __delitem__(self, key):
        try:
            del self.custom_metadata[key]
        except KeyError:
            if hasattr(self, key):
                raise AttributeError("Cannot delete built-in attributes")
