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

from abc import abstractmethod, ABC

from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video_metadata import VideoMetadata


class CompositeVideoBuilderStrategy(ABC):
    """
    Composite video builder strategy is the base class for strategies to build composite videos:

    Some strategies will target maximul quality while others will get video faster for a quick preview
    """

    @abstractmethod
    def execute(
        self, composite_video: "CompositeVideo", build_settings: VideoBuildSettings
    ):
        """
        Execute the composite video builder strategy

        We need to use hints as strings to prevent circular dependencies

        Args:
            composite_video (CompositeVideo): The composite video
            build_settings (VideoBuildSettings): The build settings

        Returns:
            CompositeVideo: The composite video
        """

    def _get_ratio_to_multiply_animations(
        self, build_settings, video_composite: "CompositeVideo"
    ):
        # Now we box the video composing this composite into the expected length, typically the one of a prompt
        if build_settings.expected_length is None:
            if build_settings.prompt is not None:
                ratioToMultiplyAnimations = (
                    video_composite.get_duration()
                    / build_settings.prompt.get_duration()
                )
            else:
                ratioToMultiplyAnimations = 1
        else:
            if build_settings.expected_length <= 0:
                raise ValueError(
                    f"Expected length should be greater than 0. Got {build_settings.expected_length}"
                )
            ratioToMultiplyAnimations = (
                video_composite.get_duration() / build_settings.expected_length
            )

        return ratioToMultiplyAnimations

    def _process_gen_vid_bins(self, args):
        """
        Process the video generation binaries: we actually do ask the video to build itself
        as a video binary (typically an MP4 generated from Gen AI, hosted behind an API),
        or to compose from its inner videos in case of a child composite video

        Args:
            args: The arguments: video, build_settings, video.media_url, target_file_name

        Returns:
            CompositeVideo: The composite video
        """
        video, build_settings, _, _ = args

        video_build = video.build(build_settings=build_settings)
        VideoMetadata(video_build.metadata).is_video_generated = True

        assert video is not None, "Video cannot be None"
        assert video.media_url is not None, "Video media URL cannot be None"

        return video_build
