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
import os
import shutil
import uuid as uid
import random

from loguru import logger

from vikit.wrappers.ffmpeg_wrapper import (
    get_media_duration,
    get_first_frame_as_image_ffmpeg,
    get_last_frame_as_image_ffmpeg,
)
from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video_metadata import VideoMetadata
from vikit.common.handler import Handler
from vikit.video.video_file_name import VideoFileName
from vikit.common.file_tools import (
    is_valid_path,
    download_or_copy_file,
    is_valid_filename,
)
from vikit.video.building.video_building_pipeline import VideoBuildingPipeline

DEFAULT_VIDEO_TITLE = "no-title-yet"


class Video(ABC):
    """
    Video is a class that helps to manage video files, be it a small video to be mixed or the final one.

    - it stores metadata about itself amd possibly subvideos
    - Video is actually really generated when you do call the build method. This is an immutable operation, i.e. once built, you cannot rebuild or change the properties of the video object.

    """

    def __init__(self, width: int = 512, height: int = 320):
        """
        Initialize the video

        Args:
            width (int): The width of the video
            height (int): The height of the video


        Raises:
            ValueError: If the source media URL is not set

        """
        self._width = width
        self._height = height
        self._background_music_file_name = None
        self._duration = None
        self._is_video_built = False
        self._needs_video_reencoding: bool = False
        self.temp_id = random.getrandbits(
            16
        )  # used to get a short ID when mixed within local filesystem filenames
        self._short_type_name = (
            "Video"  # a 5 letters identifier to easily identify the type of video
        )
        self._videoMetadata = VideoMetadata(
            id=uid.uuid4(),
            title=DEFAULT_VIDEO_TITLE,
            duration=0,
            width=self._width,
            height=self._height,
        )
        self._source = None
        self.media_url = None
        self.build_settings: VideoBuildSettings = VideoBuildSettings()
        self.are_build_settings_prepared = False
        self.video_dependencies = (
            []
        )  # Define video dependencies, i.e. the videos that are needed to build the current video

    def __str__(self):
        return f"ID:  {self.id}, type: {type(self)}, short_type_name: {self.short_type_name} , title: {self.title}, duration: {self.duration}, is_video_built: {self.is_video_built}"

    @property
    def metadata(self):
        return self._videoMetadata

    @property
    @abstractmethod
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        return self._short_type_name

    @property
    def width(self):
        return self.metadata.width

    @property
    def height(self):
        return self.metadata.height

    @property
    def id(self) -> str:
        return str(self.metadata.id)

    @property
    def background_music(self):
        return self._background_music_file_name

    @background_music.setter
    def background_music(self, file_name):
        self._background_music_file_name = file_name
        self.metadata.is_bg_music_generated = True

    @property
    def duration(self):
        return self.metadata.duration

    @duration.setter
    def duration(self, value):
        self._duration = value
        self.metadata.duration = value

    @property
    def is_video_built(self):
        return self._is_video_built

    @is_video_built.setter
    def is_video_built(self, value):
        self._is_video_built = value
        self.metadata.is_video_built = value

    @property
    def title(self):
        return self.get_title()

    @title.setter
    def title(self, value):
        self.metadata.title = value

    @abstractmethod
    def get_title(self):
        """
        Returns the title of the video.
        """
        return "no-title-yet" if self.metadata.title is None else self.metadata.title

    async def get_first_frame_as_image(self):
        """
        Get the first frame of the video
        """
        target_path = f"fst_frm_{self.id}.jpg"

        return await get_first_frame_as_image_ffmpeg(
            media_url=self.media_url, target_path=target_path
        )

    async def get_last_frame_as_image(self):
        """
        Get the last frame of the video
        """
        target_path = f"lst_frm_{self.id}.jpg"

        return await get_last_frame_as_image_ffmpeg(
            media_url=self.media_url, target_path=target_path
        )

    def get_duration(self):
        """
        Get the duration of the final video

        Returns:
            float: The duration of the final video
        """
        if self.media_url is None:
            raise ValueError("The source media URL is not set")
        self.duration = float(get_media_duration(self.media_url))
        return self._duration

    def _set_working_folder_dir(self, working_folder_path: str):
        if working_folder_path:
            if is_valid_path(working_folder_path):
                os.chdir(working_folder_path)
                return True
            else:
                logger.warning(
                    f"Video target dir path name is None or invalid, using the current video generation path: {os.getcwd()}"
                )
                return False

    def build(self, build_settings: VideoBuildSettings = VideoBuildSettings()):
        """
        Build in async but expose a sync interface
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If there's already a running loop, create a new task and wait for it
            return loop.create_task(self.build_async(build_settings))
        else:
            # If no loop is running, use asyncio.run
            return asyncio.run(self.build_async(build_settings))

    async def build_async(
        self, build_settings: VideoBuildSettings = VideoBuildSettings()
    ):
        """
        Build the video in the child classes, unless the video is already built, in  which case
        we just return ourseleves (Video gets immutable once generated)

        This is a template method, the child classes should implement the get_handler_chain method

        Args:
            build_settings (VideoBuildSettings): The settings to use for building the video

        Returns:
            Video: The built video

        """
        if self._is_video_built:
            logger.info(f"Video {self.id} is already built, returning itself")
            return self

        current_dir = os.getcwd()
        logger.trace(
            f"Starting the pre build hook for Video {self.id}, current_dir {current_dir} "
        )

        wfolder_changed = self._set_working_folder_dir(build_settings.output_path)
        logger.trace(f"Working folder has changed? : {wfolder_changed}")

        logger.trace(
            f"Starting the pre build hook for Video {self.id} of type {self.short_type_name} / {type(self)}"
        )
        await self.run_pre_build_actions_hook(build_settings=build_settings)

        built_video = None
        if not self.are_build_settings_prepared:
            self.build_settings = build_settings
            self._source = type(
                build_settings.get_ml_models_gateway()  # TODO: this is hacky anbd should be refactored
                # so that we infer source from the different handlers (initial video generator, interpolation, etc)
            ).__name__  # as the source(s) of the video is used later to decide if we need to reencode the video

            await self.prepare_build(build_settings=build_settings)
            self.are_build_settings_prepared = True

        logger.info(f"Starting the building of Video {self.id} ")

        built_video = await self.run_build_core_logic_hook(
            build_settings=build_settings
        )  # logic from the child classes if any
        built_video = await self.gather_and_run_handlers()

        logger.debug(f"Starting the post build hook for Video {self.id} ")
        await self.run_post_build_actions_hook(build_settings=build_settings)

        if self.build_settings.target_file_name:
            self.set_final_video_name(
                output_file_name=build_settings.target_file_name,
            )

        if wfolder_changed:
            self._set_working_folder_dir(
                current_dir
            )  # go back to the original working folder

        self.is_video_built = True

        return built_video

    async def gather_and_run_handlers(self):
        """
        Gather the handler chain and run it
        """
        logger.trace("Gathering the handler chain")
        built_video = None

        handler_chain = self._get_and_initialize_video_handler_chain(
            build_settings=self.build_settings
        )
        if not handler_chain:
            logger.warning(
                f"No handler chain defined for the video of type {self.short_type_name}"
            )
        else:
            logger.debug(
                f"about to run {len(handler_chain)} handlers for video {self.id} of type {self.short_type_name} / {type(self)}"
            )
            for handler in handler_chain:
                built_video = await handler.execute_async(video=self)
                built_video.is_video_built = True

                assert built_video.media_url, "The video media URL is not set"

        self.metadata.title = self.get_title()
        self.media_url = await download_or_copy_file(
            url=self.media_url,
            local_path=self.get_file_name_by_state(self.build_settings),
        )
        self.metadata.duration = (
            self.get_duration()
        )  # This needs to happen once the video has been downloaded

        return built_video

    async def run_build_core_logic_hook(self, build_settings: VideoBuildSettings):
        """
        Run the core logic of the video building

        Args:
            build_settings (VideoBuildSettings): The settings to use for building the video
        """

    async def run_pre_build_actions_hook(self, build_settings: VideoBuildSettings):
        """
        Pre build actions hook

        Args:
            build_settings (VideoBuildSettings): The settings to use for building the video
        """

    async def run_post_build_actions_hook(self, build_settings: VideoBuildSettings):
        """
        Post build actions hook
        """

    async def prepare_build(self, build_settings: VideoBuildSettings) -> "Video":
        """
        Prepare the video for building, may be used to inject build settings for individual videos
        that we don't want to share with global buildsettings. For instance to generate a video
        a given way, and another video another way, all in the same composite video

        Args:
            build_settings (VideoBuildSettings): The settings to use for building the video later on

        returns:
            Video: The current instance, prepared for building
        """
        logger.debug(
            f"Preparing the build settings with {build_settings} for video {self.id} of type {self.short_type_name} / {type(self)}"
        )
        self.build_settings = build_settings
        self.are_build_settings_prepared = True

        return self

    def set_final_video_name(self, output_file_name: str):
        """
        Rename the video media file to the output_file_name if not already set
        as the current media file.

        Todday this function only works for local files.

        We fail open: in case no target file name works, we just keep the video
        as it is and where it stands. We send a warning to the logger though.

        Args:
            output_file_name (str): The output file name

        Returns:
            The video with the target file name
        """
        current_file_name = os.path.basename(self.media_url)
        # We should already be positionned in the right target folder
        if current_file_name != output_file_name:
            new_file_path = output_file_name
            logger.debug(
                f"Copying video media file from {self.media_url} to {new_file_path}"
            )
            if not is_valid_filename(output_file_name):
                raise ValueError(
                    f"Invalid output file name: {output_file_name}, cannot rename the video media file"
                )
            try:
                shutil.copyfile(
                    self.media_url,
                    new_file_path,
                )
                self.media_url = new_file_path
            except Exception as e:
                logger.warning(
                    f"Could not copy the video media file to the target file name: {e}"
                )

    def get_file_name_by_state(self, build_settings: VideoBuildSettings = None):
        """
        Get the file name of the video by its state

        Shortcut method not to have to call the VideoFileName class directly
        """
        assert self.metadata, "metadata should be set"
        if not build_settings and not self.build_settings:
            raise ValueError("build_settings should be set")

        infered_name = str(
            VideoFileName(
                video_type=self.short_type_name,
                video_metadata=self.metadata,
                build_settings=(
                    self.build_settings if not build_settings else build_settings
                ),
            )
        )
        logger.debug(
            f"Video file name inferred: {infered_name}, current media URL: {self.media_url}"
        )
        return infered_name

    def generate_background_music_prompt(self):
        """
        Get the background music prompt from the video list.

        returns:
            str: The background music prompt
        """
        return self.get_title()

    def _get_and_initialize_video_handler_chain(
        self, build_settings: VideoBuildSettings
    ) -> list[Handler]:
        """
        Get the handler chain of the video.
        Defining the handler chain is the main way to define how the video is built
        so it is up to the child classes to implement methods called by this template method

        Args:
            build_settings (VideoBuildSettings): The settings to use for building the video

        Returns:
            list: The list of handlers to use for building the video
        """
        handlers = []

        handlers.extend(self.get_core_handlers(build_settings))
        handlers.extend(
            VideoBuildingPipeline().get_handlers(self, build_settings=build_settings)
        )
        logger.debug(
            f"Handlers for video {self.id} of type {type(self)} / {self.short_type_name}: {handlers}"
        )

        return handlers

    def get_core_handlers(self, build_settings=None):
        """
        Get the core handlers for the video
        """
        return []
