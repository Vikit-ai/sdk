import subprocess
import os
from abc import abstractmethod, ABC
import uuid as uid
import asyncio

from loguru import logger

from vikit.common.decorators import log_function_params
import vikit.common.config as config
from vikit.wrappers.ffmpeg_wrapper import (
    get_media_duration,
    extract_audio_slice,
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

    def get_first_frame_as_image(self):
        """
        Get the first frame of the video
        """
        assert self.media_url, "no media URL provided"
        assert os.path.exists(self.media_url), "The video file does not exist yet"

        result_path = ft.create_non_colliding_file_name(
            canonical_name="fst_frm_" + self.get_title()[0], extension=".jpg"
        )
        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                self.media_url,
                "-vf",
                "select=eq(n\\,0)",  # c'est un filtre vidéo qui sélectionne les frames à extraire. eq(n\,0)
                # signifie qu'il sélectionne la frame où n (le numéro de la frame) est égal à 0, c'est-à-dire la première frame
                "-vframes",  # spécifie le nombre de frames vidéo à sortir
                "1",  # on veut une seule frame
                result_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result.check_returncode()
        return result_path

    def get_last_frame_as_image(self):
        """
        Get the last frame of the video
        """
        assert self.media_url, "no media URL provided"
        assert os.path.exists(self.media_url), "The video file does not exist"

        result_path = ft.create_non_colliding_file_name(
            canonical_name="last_frm_" + self.get_title()[0], extension=".jpg"
        )
        result = subprocess.run(
            [
                "ffmpeg",
                "-sseof",  # spécifie qu'il doit commencer à x secondes de la fin du fichier.
                "-3",  # on veut les 3 dernières secondes
                "-i",
                self.media_url,
                "-update",  # signifie qu'il doit mettre à jour l'image de sortie si x nouvelle frame est disponible.
                "1",  # on veut une seule frame
                "-q:v",  # -q:v 1 spécifie la qualité de l'image de sortie (1 étant la meilleure qualité).
                "1",
                result_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result.check_returncode()
        return result_path

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

        self.prepare_build(build_settings=build_settings)

        handler_chain = self.get_handler_chain()
        built_video = await handler_chain[0].execute(video=self)

        self._is_video_generated = True
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
        self.are_build_settings_prepared = True

    @log_function_params
    def _fit_standard_background_music(self, expected_music_duration: float = None):
        """
        Prepare a standard background music for the video

        Args:
            expected_music_duration (float): The expected duration of the music
            In case the audio is shorter, we will just stop playing music when it ends, no music looping for now

        """
        return extract_audio_slice(
            start=0,
            end=expected_music_duration,
            audiofile_path=config.get_default_background_music(),
            target_file_name=self._get_bk_music_target_filemame(),
        )

    @log_function_params
    def _get_bk_music_target_filemame(self):
        """
        Get the target file name for the background music
        """
        return f"{self.media_url[:-4].split('/')[-1]}_background_music.mp3"

    async def _build_background_music(
        self, build_settings: VideoBuildSettings, prompt_text: str = ""
    ):
        """
        Prepare background music for the video either by
        - using a slice of standard background music,
        - using a slice of the existing video background music file
        - generating it using an LLM (not implemented yet)

        Args:
            build_settings (VideoBuildSettings): The settings to use for building
            prompt_text (str): The prompt text to use for generating the music

        Returns:
            str: The path to the generated background music
        """
        logger.debug(f"self.background_music:: {self.background_music:}")

        if build_settings.music_building_context.generate_background_music:
            self._background_music_file_name = asyncio.run(
                self._generate_music(
                    expected_music_length=self.get_duration(),
                    test_mode=build_settings.test_mode,
                    prompt_text=prompt_text,
                )
            )
            self.metadata.is_bg_music_generated = True
        else:
            if self.background_music:
                if not os.path.exists(self.background_music):
                    raise ValueError("background_music does not exists")
                # Now we check the length , we may loop the background music in a future version
                if get_media_duration(self.background_music) < self.get_duration():
                    raise ValueError(
                        "The given background music is too short for the video"
                    )

                extract_audio_slice(
                    start=0,
                    end=self.get_duration(),
                    audiofile_path=self.background_music,
                    target_file_name=self.self._background_music_file_name,
                )
            else:  # use the standard bg music
                self._background_music_file_name = self._fit_standard_background_music(
                    expected_music_duration=build_settings.music_building_context.expected_music_length
                )

        self._is_background_music_generated = True

        return self._background_music_file_name

    async def _generate_music(
        self,
        expected_music_length,
        prompt_text: str = None,
    ):
        """
        Generate the background music for the video

        Args:
            expected_music_length (float): The expected length of the music
            prompt_text (str): The prompt text to use for generating the music
            test_mode (bool): The test mode

        Returns:
            str: The path to the generated background music
        """
        return await self.build_settings.get_ml_models_gateway().generate_background_music_async(
            duration=expected_music_length, prompt=prompt_text
        )

    @abstractmethod
    def get_video_handler_chain(
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
        pass
