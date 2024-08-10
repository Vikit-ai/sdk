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

import datetime
import os
import random

from loguru import logger

from vikit.common.file_tools import get_max_path_length
from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video_metadata import VideoMetadata

MANAGED_FEATURES = "dogrvip"
split_separator = "__"


class VideoFileName:
    """
    Class for Video file name manipulation.

    A video file name is a string that represents the name of a video file.
    It respects a convention that is used to identify the video file easily

    Complementary metadata may exist in additional stores, however, the file name is the primary identifier
    and the bare minimum is here to simplify processing even if the metadata store is not available
    """

    VIDEO_TITLE_MAX_LENGTH = 20

    def __init__(
        self,
        build_settings: VideoBuildSettings,
        video_metadata: VideoMetadata,
        video_type: str = None,
        video_features: str = None,
        file_extension: str = "mp4",
    ):
        """
        Initializes the file name with the metadata

        params:
            build_settings: The build settings of the video: provides the build id, the build date and the build time
            video_metadata: The metadata of the video, provides the actual features of the video
            video_type: The type of video, 10 digits max, string like comp-root, comp-child, transition, etc.

            video_features: The features of the video, uses 5 bytes max:
                - 1st digit:
                    - 'd' if the video includes the default background music,
                    - 'g' if the video includes the generated background music,
                    - 'p' if the video uses the prompt original recording as background music,
                    - 'o' if the video does not include  background music,
                - 2nd digit: 'v' if the video includes voice over from subtitles, 'o' otherwise
                - 3rd digit: 'r' if the video has been reencoded, 'o' otherwise
                - 4th digit: 'i' if the video has been interpolated, o otherwise
                - 5th digit: free to use

            file_extension: The file extension of the video, uses 3 digits max
        """
        if video_metadata is None:
            raise ValueError("video_metadata cannot be None")
        self._video_metadata = video_metadata
        self.title = self._truncate_title(
            video_metadata.title, max_length=self.VIDEO_TITLE_MAX_LENGTH
        )
        self._video_type = video_type if video_type is not None else "undefined"
        if build_settings is None:
            raise ValueError("build_settings cannot be None")
        self._build_settings = build_settings

        self._build_id = build_settings.id
        self._build_date = build_settings.build_date
        self._video_temp_id = str(video_metadata.temp_id)
        self._file_extension = file_extension
        self._file_name = None

        self._video_features = None
        if not video_features:
            self._is_reencoded = video_metadata.is_reencoded
            self._has_default_background_music = video_metadata.bg_music_applied
            self._has_generated_background_music = video_metadata.is_bg_music_generated
            self._uses_recorded_prompt_as_audio = (
                video_metadata.is_subtitle_audio_applied
            )
            self._has_been_interpolated = video_metadata.is_interpolated
            self._is_prompt_read_aloud = video_metadata.is_prompt_read_aloud
            self._video_features = self.extract_features_as_string()
        else:
            self._video_features = video_features
            self.infer_features()

    def infer_features(self):
        """
        Infer the features from the video features string

        In case unknown features are found, a warning is logged
        """
        self._has_default_background_music = self._video_features[0] == "d"
        self._has_generated_background_music = self._video_features[0] == "g"
        self._uses_recorded_prompt_as_audio = self._video_features[0] == "p"

        self._is_prompt_read_aloud = self._video_features[1] == "v"

        self._is_reencoded = self._video_features[2] == "r"
        self._has_been_interpolated = self._video_features[3] == "i"

    @staticmethod
    def from_file_name(file_name: str):
        """
        Parse a file name to extract the metadata

        params:
            file_name: The file name to parse

        returns:
            VideoFileName: The video file name object
        """

        parts = file_name.split("__")
        title = parts[0]
        bld_settings = VideoBuildSettings()
        bld_settings.id = parts[3]
        date_str = parts[4]
        if date_str.endswith(".mp4"):
            date_str = date_str[:-4]
        bld_settings.build_date = datetime.date.fromisoformat(date_str)
        video_file_name = VideoFileName(
            build_settings=bld_settings, video_metadata=VideoMetadata(title=title)
        )
        video_file_name._video_type = parts[1]
        video_file_name._video_features = parts[2]

        return video_file_name

    def extract_features_as_string(self):
        """
        Extract the features from the video features string
        """
        if (
            self._video_features
        ):  # if the video features are already set, we return them
            return self._video_features

        features_as_string = "ooooo"

        if self._has_default_background_music:
            features_as_string = "d" + features_as_string[1:]
        if self._has_generated_background_music:
            features_as_string = "g" + features_as_string[1:]
        if self._uses_recorded_prompt_as_audio:
            features_as_string = "p" + features_as_string[1:]

        if self._is_prompt_read_aloud:
            features_as_string = features_as_string[0] + "v" + features_as_string[2:]

        if self._is_reencoded:
            features_as_string = features_as_string[:2] + "r" + features_as_string[3:]

        if self._has_been_interpolated:
            features_as_string = features_as_string[:3] + "i" + features_as_string[4:]

        assert len(features_as_string) == 5

        return features_as_string

    @property
    def video_type(self):
        """
        Get the type of the video, codified as a string

        Examples:
        - comproot: A composite video that is the root of a tree of composite videos
        - compchild: A composite video that is a child of a tree of composite videos
        - transition: A transition video
        - imported: A video imported from an external source
        - rawtext: A video generated from short raw text (usually a few words, like a sentence)

        The video type is not strongly typed so you may add up easily new types, though
        you may leverage video_type enum to keep close to our defacto standards.
        """
        return self._video_type

    @property
    def build_id(self):
        return str(self._build_id)

    @property
    def file_name(self):
        """
        Get the file name of the video,  as a string
        """
        if self._file_name:
            return self._file_name

        # file_name = f"{self.title}oOo{str(self.video_type)}oOo{self.video_features}oOo{self.build_id}oOo{self._build_date}oOoUIDoOo{self._video_temp_id}.{self._file_extension}"
        file_name = f"{self.title}oOo{str(self.video_type)}oOo{self.video_features}oOo{self.build_id}oOo{self._build_date}.{self._file_extension}"
        file_name = file_name.replace("oOo", split_separator)
        logger.debug(f"file name by state to be returned: {file_name} ")
        self._file_name = file_name
        return self._file_name

    def __str__(self):
        return self._fit(target_path=self._build_settings.output_path)

    def __repr__(self):
        return f"Title: {self.title}, Video Type: {self._video_type}, Video Features: {self._video_features} , Build ID: {self._build_id}, Build Date: {self._build_date}"

    @property
    def video_features(self):
        return self._video_features

    @property
    def length(self):
        return len(self.file_name)

    def _truncate_title(self, title: str, max_length: int = 30):
        """
        Truncate the title of the video

        params:
            title: The title to be truncated
            max_length: The maximum length of the title

        returns:
            str: The truncated title
        """
        if len(title) > max_length:
            # first we make it so the title is clean, not taking back the video features string
            title = title.split(split_separator)[0]
            return title[:max_length]
        return title

    def truncate(self, gap: int):
        """
        Truncate the file name to fit the file system's limits

        params:
        gap: The gap between the file name's length and the file system's limits

        36 is the length of the UUID, 4 is the length of the file extension

        returns:
        str: The truncated file name
        """
        return (
            self.file_name[: len(self.file_name) - gap - 36 - 4]
            + "."
            + self._file_extension
        )

    def _fit(self, target_path: str = None):
        """
        Infer a file name that fits the file system max path length,  factoring in the target path's length
        This means we may we reduce the length of the file name to let room for the random suffix if needed

        params:
            target_path: the path where the file will be saved

        return: the fitted file name
        """
        if target_path is None:
            target_path = os.getcwd()

        if self.length + len(target_path) >= get_max_path_length():
            logger.warning(
                f"The file name is too long, it will be truncated to fit the file system's limits. Target path {target_path}",
            )
            # So we may truncate the file name as long as we keep a UUID, we may also afford to lose
            # the build id, the date and the time
            logger.debug(
                f"target path length: {len(target_path)}, len(self.file_name): {len(self.file_name)}"
            )
            logger.debug(f"target path: {target_path}, file name: {self.file_name}")

            gap = get_max_path_length() - len(self.file_name) - len(target_path)
            if (
                abs(gap) > 25 + 10 + 10 + 6
            ):  # 25 is the length of the title we can lose,
                # 10 is the length of the build id, 10 is the length of the date, 6 is the length of the time
                raise ValueError(
                    f"The file name is too long, it cannot be truncated, gap: {gap}"
                )
            else:
                fitted_name = self.truncate(gap)
                logger.warning(
                    f"The file name has been truncated to fit the file system's limits. New file name: {fitted_name}",
                )
        else:
            fitted_name = self.file_name

        return fitted_name
