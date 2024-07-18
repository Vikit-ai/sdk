import subprocess
import os
from abc import abstractmethod, ABC
import uuid as uid

from loguru import logger

from vikit.common.decorators import log_function_params
from vikit.wrappers.ffmpeg_wrapper import (
    get_media_duration,
    get_first_frame_as_image_ffmpeg,
    get_last_frame_as_image_ffmpeg,
)
from vikit.video.video_build_settings import VideoBuildSettings
import vikit.common.file_tools as ft
from vikit.video.video_file_name import VideoFileName
from vikit.video.video_metadata import VideoMetadata
from vikit.video.building.video_building_handler import VideoBuildingHandler


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
        self._is_video_generated = False
        self._needs_reencoding: bool = None
        self._id = uid.uuid4()
        self.top_parent_id = (
            self._id
        )  # The top parent id is the id of the video that is the top parent of the current video chain, if any
        self._short_type_name = (
            "Video"  # a 5 letters identifier to easily identify the type of video
        )
        self._videoMetadata = VideoMetadata(
            id=self._id,
            title="notitle-yet",
            duration=0,
            width=self._width,
            height=self._height,
            is_video_generated=False,
            is_reencoded=False,
            is_interpolated=False,
            is_bg_music_applied=False,
            is_bg_music_generated=None,  # if not using gnerated we infer the default bg music is used
            top_parent_id=self.top_parent_id,
        )

        self.media_url = None
        self.build_settings = None
        self.are_build_settings_prepared = False
        self.video_dependencies = (
            []
        )  # Define video dependencies, i.e. the videos that are needed to build the current video

    @property
    def metadata(self):
        return self._videoMetadata

    @metadata.setter
    def metadata(self, metadata):
        if not isinstance(metadata, VideoMetadata):
            raise ValueError("metadata should be of type VideoMetadata")
        self._videoMetadata = metadata

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

    @property
    def duration(self):
        return self.metadata.duration

    @property
    def is_video_generated(self):
        return self.metadata.is_video_generated

    @property
    def title(self):
        return self.get_title()

    def get_file_name_by_state(
        self,
        build_settings: VideoBuildSettings,
        metadata: VideoMetadata = None,
        video_type: str = None,
    ):
        """
        Get the file name of the video depending on the current metadata / vide state

        params:
            build_settings (VideoBuildSettings): used to gather build contextual information
            metadata (VideoMetadata): The metadata to use for generating the file name
            video_type (str): The type of the video

        Returns:
            str: The file name of the video
        """
        if not metadata:
            metadata = self.metadata

        vid_type = video_type if video_type else self.short_type_name

        video_fname = VideoFileName(
            video_type=vid_type,
            video_metadata=metadata,
            build_settings=build_settings,
        )
        return str(video_fname)

    @abstractmethod
    def get_title(self):
        """
        Returns the title of the video.
        """
        return "notitle"

    async def get_first_frame_as_image(self):
        """
        Get the first frame of the video
        """
        target_path = ft.create_non_colliding_file_name(
            canonical_name="fst_frm_" + self.get_title()[0], extension=".jpg"
        )

        return await get_first_frame_as_image_ffmpeg(
            media_url=self.media_url, target_path=target_path
        )

    async def get_last_frame_as_image(self):
        """
        Get the last frame of the video
        """
        target_path = ft.create_non_colliding_file_name(
            canonical_name="lst_frm_" + self.get_title()[0], extension=".jpg"
        )

        return await get_last_frame_as_image_ffmpeg(
            media_url=self.media_url, target_path=target_path
        )

    @log_function_params
    def get_duration(self):
        """
        Get the duration of the final video

        Returns:
            float: The duration of the final video
        """
        if self._duration is None:
            if self.media_url is None:
                raise ValueError("The source media URL is not set")
            self._duration = float(get_media_duration(self.media_url))
        return self._duration

    async def build(self, build_settings: VideoBuildSettings = None):
        """
        Build the video in the child classes, unless the video is already built, in  which case
        we just return ourseleves (Video gets immutable once generated)

        This is a template method, the child classes should implement the get_handler_chain method

        Args:
            build_settings (VideoBuildSettings): The settings to use for building the video

        Returns:
            Video: The built video

        """
        if self._is_video_generated:
            return self
        built_video = None
        self.prepare_build(build_settings=build_settings)

        handler_chain = self.get_and_initialize_video_handler_chain(
            build_settings=self.build_settings
        )
        if not handler_chain:
            logger.warning(
                f"No handler chain defined for the video of type {self.short_type_name}"
            )
        else:
            for handler in handler_chain:
                if handler.is_supporting_async_mode():
                    built_video, _ = await handler.execute_async(video=self)
                else:
                    built_video = handler.execute(video=self)

            self.run_post_build_actions()

        return built_video

    def run_post_build_actions(self):
        """
        Ppost build actions hook
        """
        pass

    @abstractmethod
    async def prepare_build(self, build_settings: VideoBuildSettings):
        """
        Prepare the video for building, may be used to inject build settings for individual videos
        that we don't want to share with global buildsettings. For instance to generate a video
        a given way, and another video another way, all in the same composite video

        Args:
            build_settings (VideoBuildSettings): The settings to use for building the video later on

        Returns:
            Video: The prepared video
        """
        self.build_settings = build_settings
        self._source = type(
            build_settings.get_ml_models_gateway()  # TODO: this is hacky anbd should be refactored
            # so that we infer source from the different handlers (initial video generator, interpolation, etc)
        ).__name__  # as the source(s) of the video is used later to decide if we need to reencode the video
        self.are_build_settings_prepared = True

    @log_function_params
    def _get_bk_music_target_filemame(self):
        """
        Get the target file name for the background music
        """
        return f"{self.media_url[:-4].split('/')[-1]}_background_music.mp3"

    @abstractmethod
    def get_and_initialize_video_handler_chain(
        self, build_settings: VideoBuildSettings
    ) -> list[VideoBuildingHandler]:
        """
        Get the handler chain of the video.
        Defining the handler chain is the main way to define how the video is built
        so it is up to the child classes to implement this method as a complement
        of this music building logic, or to redefine it.

        Args:
            build_settings (VideoBuildSettings): The settings to use for building the video

        Returns:
            list: The list of handlers to use for building the video
        """
        return []
