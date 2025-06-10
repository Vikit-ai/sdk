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

import asyncio
import os
import uuid as uid

from loguru import logger

from vikit.music_building_context import MusicBuildingContext
from vikit.video.building.build_order import (
    get_lazy_dependency_chain_build_order,
    is_composite_video,
)
from vikit.video.video import DEFAULT_VIDEO_TITLE, Video
from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video_types import VideoType
from vikit.wrappers.ffmpeg_wrapper import concatenate_videos, get_media_duration


class CompositeVideo(Video, is_composite_video):
    """
    Composite made from the collection of videos that need to be generated altogether, as a consistent block

    It could be a final video or intermediate  composing specific scenes of the final video.

    Composite video can include other composite videos, and so on, to build a tree of videos to be generated
    """

    def __init__(self):
        """
        We can initialize a VideoComposite using a subtitle to work on it
        and help set the right length for the appended videos or video composites
        and to be generated as a single block
        """
        super().__init__()

        self.composite_video_uuid = str(uid.uuid4())

        self.is_root_video_composite = True  # true until we have a composite video that will add this composite as a child using append
        self.video_list = []

    def is_composite_video(self):
        return True

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        if self.is_root_video_composite:
            return str(VideoType.COMPROOT)
        else:
            return str(VideoType.COMPCHILD)

    def __str__(self):
        videos_output = (
            os.linesep
            + super().__str__()
            + os.linesep
            + "----- Composite video video list-----"
            + os.linesep
        )
        for video in self.video_list:
            videos_output = videos_output + str(video) + os.linesep

        return f"{videos_output}"

    def get_children_build_settings(self):
        """
        Get the  build settings for children Video
        """
        logger.debug(
            f"Composite video {self.id} getting children build settings from {self.build_settings}"
        )
        if self.build_settings.cascade_build_settings:
            return self.build_settings
        else:
            return VideoBuildSettings(
                interpolate=self.build_settings.interpolate,
                include_read_aloud_prompt=False,
                music_building_context=MusicBuildingContext(
                    apply_background_music=False
                ),
                target_model_provider=self.build_settings.target_model_provider,
                vikit_api_key=self.build_settings.vikit_api_key,
                aspect_ratio=self.build_settings.aspect_ratio,
                is_good_until=self.build_settings.is_good_until,
                max_attempts=self.build_settings.max_attempts,
                prompt_updater_fn=self.build_settings.prompt_updater_fn,
            )

    def append_video(self, video: Video):
        """
        Append a video to the list of videos to be mixed

        params:
            video: The video to be appended

        returns:
            self: The current object
        """
        if not video:
            raise ValueError("video cannot be None")
        self.video_list.append(video)
        self.video_dependencies.append(video)

        if video._needs_video_reencoding:  # Adding a video that needs reencoding will trigger reencoding of the whole tree
            self._needs_video_reencoding = True

        if isinstance(video, CompositeVideo):
            logger.debug(
                f"experiment  1 composite video {video.id} to composite video {self.id}"
            )
            video.is_root_video_composite = False

        return self

    def get_duration(self):
        """
        Get the duration of the video, we recompute it every time
        as the duration of the video can change if we add or remove videos
        """
        if self.metadata.is_video_built:
            return self.metadata.duration
        else:
            all_video_duration = 0
            for video in self.video_list:
                all_video_duration += video.get_duration()
            self._duration = all_video_duration

            self.metadata.duration = all_video_duration
            return all_video_duration

    def get_title(self):
        """
        Get the title of the video, we recompute it every time
        as the title of the video can change if we add or remove videos
        """
        title = "_".join([subvideo.get_title() for subvideo in self.video_list])
        self._title = "empty-composite" if title == "" else title
        self.metadata.title = self._title
        return self._title

    def update_metadata_post_building(self):
        """
        Update the metadata post building
        """
        nb_interpolated = len(
            list(
                filter(
                    lambda builtvideo: builtvideo.metadata.is_interpolated,
                    self.video_list,
                )
            )
        )
        if nb_interpolated < len(self.video_list):
            self.metadata.is_interpolated
        elif nb_interpolated == 0:
            self.metadata.is_interpolated = False
            # TODO: handle partially interpolated videos, not really important for now

    def cleanse_video_list(self):
        """
        Cleanse the video list by removing any empty composites videos
        """
        return list(
            filter(
                lambda video: not (
                    isinstance(video, CompositeVideo) and len(video.video_list) == 0
                ),
                self.video_list,
            )
        )

    async def run_pre_build_actions_hook(self, build_settings: VideoBuildSettings):
        self.video_list = self.cleanse_video_list()

    async def run_build_core_logic_hook(
        self,
        ml_models_gateway,
        build_settings=VideoBuildSettings(),
    ):
        """
        Mix all the videos in the list: here we actually build and stitch the videos together,
        will take some time and resources as we call external services and run video mixing locally.

        Warning: order is very important here, and the first pass is supposed to happen from the root composite levels

        Today we do generate the videos so the first ones are the ones that will be used to generate the final video
        This requires a specific order, and generating videos ahead of time won't work unless you take care
        of building the videos in the child composite video list first.

        params:
            build_settings: The settings to be used for the build

        Returns:
            self: The current object
        """
        if (
            self.is_root_video_composite
        ):  # This check is important: we generate an ordered video list
            # for the whole video tree at once
            ordered_video_list = get_lazy_dependency_chain_build_order(
                video_tree=self.video_list,
                build_settings=build_settings,
                already_added=set(),
            )
            no_dependency_videos = [
                v for v in ordered_video_list if not v.video_dependencies
            ]
            await asyncio.gather(
                *(
                    v.build(
                        self.get_children_build_settings(),
                        ml_models_gateway=ml_models_gateway,
                    )
                    for v in no_dependency_videos
                )
            )
            with_dependency_videos = [
                v for v in ordered_video_list if v.video_dependencies
            ]
            # Repeat the process until all videos are processed.
            while with_dependency_videos:
                tasks = []
                for video in with_dependency_videos[:]:
                    dependencies_processed = all(
                        dep._is_video_built for dep in video.video_dependencies
                    )
                    if dependencies_processed:
                        tasks.append(
                            video.build(
                                build_settings=self.get_children_build_settings(),
                                ml_models_gateway=ml_models_gateway,
                            )
                        )
                        with_dependency_videos.remove(video)

                if tasks:
                    await asyncio.gather(*tasks)
                else:
                    raise Exception("Some dependencies could not be processed.")

        # at this stage we should have all the videos generated. Will be improved in the future
        # in case we are called directly on a child composite without starting by the composite root
        self.media_url = await self._build_video_binary()

        return self

    async def _build_video_binary(self):
        """
        Builds a video binary file by concatenating the videos contained in the current
        composite video list.
        """
        return await concatenate_videos(
            video_file_paths=[
                video.media_url for video in self.video_list if not video.discarded
            ],
            target_file_name=self.get_file_name_by_state(
                build_settings=self.build_settings,
            ),
            ratio_to_multiply_animations=self._get_ratio_to_multiply_animations(
                build_settings=self.build_settings
            ),
        )

    def _get_ratio_to_multiply_animations(
        self, build_settings: VideoBuildSettings
    ) -> float:
        # Now we box the video composing this composite into the expected length,
        # typically the one of a prompt
        if build_settings.expected_length is None:
            if build_settings.prompt is not None:
                logger.debug(
                    "parameters video_composite.get_duration() build_settings.prompt: "
                    f"{self.get_duration()}, {build_settings.prompt}"
                )
                ratio_to_multiply_animations = (
                    # TODO: review this code path as it is likely never used, as
                    # duration is not a member of the prompt
                    self.get_duration() / build_settings.prompt.duration
                )
            else:
                ratio_to_multiply_animations = 1
        else:
            if build_settings.expected_length <= 0:
                raise ValueError(
                    "Expected length should be greater than 0. Got "
                    f"{build_settings.expected_length}"
                )
            if self.get_duration() is None:
                raise ValueError(
                    "Composite video duration is None, cannot compute ratio. Please "
                    "ensure all videos are built."
                )
            if self.get_duration() <= 0:
                raise ValueError(
                    "Composite video duration should be greater than 0. Got "
                    f"{self.get_duration()}"
                )

            ratio_to_multiply_animations = (
                self.get_duration() / build_settings.expected_length
            )

        logger.debug(
            f"Composite video {self.id} ratio to multiply animations: "
            f"{ratio_to_multiply_animations}"
        )
        return ratio_to_multiply_animations

    async def run_post_build_actions_hook(self, build_settings: VideoBuildSettings):
        if not build_settings.target_file_name:
            if self.is_root_video_composite:
                if self.media_url is None:
                    raise ValueError("media_url is None, cannot determine file name.")
                name, extension = os.path.splitext(os.path.basename(self.media_url))
                _name = name.replace(DEFAULT_VIDEO_TITLE, "YourVideo")
                new_name = f"{_name}_{uid.uuid4()}{extension}"
                build_settings.target_file_name = os.path.join(
                    os.path.dirname(self.media_url), new_name
                )
                logger.info(
                    f"Your final video name is : {build_settings.target_file_name}"
                )
        self.metadata.duration = get_media_duration(self.media_url)

    def generate_background_music_prompt(self):
        """
        Get the background music prompt from the video list.

        returns:
            str: The background music prompt
        """
        return " ".join(
            [video.get_title() for video in self.video_list if video.get_title()]
        )
