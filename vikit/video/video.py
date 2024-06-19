import subprocess
import os
from abc import abstractmethod

from loguru import logger

from vikit.common.decorators import log_function_params
import vikit.common.config as config
from vikit.wrappers.ffmpeg_wrapper import (
    merge_audio,
    get_media_duration,
    extract_audio_slice,
)
from vikit.prompt.recorded_prompt import RecordedPrompt
from vikit.video.video_build_settings import VideoBuildSettings
import vikit.common.os_objects_naming_tools as osnamingtools
import vikit.gateways.ML_models_gateway_factory as ML_models_gateway_factory


class Video:
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
        self._duration = None
        self._media_url = None
        self._background_music_file_name = None
        self._is_video_generated = False
        self._needs_reencoding: bool = None

    @property
    def background_music(self):
        return self._background_music_file_name

    def __str__(self):
        video_as_string = os.linesep.join(
            [
                """////// Video Description \\\\\\""",
                f"Video Title: {self.get_title()}",
                f"Duration: {self._duration}",
                f"Media URL: {self.media_url}",
                f"Width: {self._width}",
                f"Height: {self._height}",
                f"is_video_generated: {self._is_video_generated}",
                f"background_music_file_name: {self._background_music_file_name}",
            ]
        )

        return os.linesep + video_as_string + os.linesep

    def get_title(self):
        """
        Returns the title of the video.
        """
        return self.media_url if self.media_url else "no title"

    @property
    def media_url(self):
        """
        Get the media URL of the video.
        """
        return self._media_url

    @log_function_params
    def get_first_frame_as_image(self):
        """
        Get the first frame of the video
        """
        assert self._media_url, "no media URL provided"
        assert os.path.exists(self.media_url), "The video file does not exist"
        result_path = (
            "first_frame_video_"
            + osnamingtools.create_non_colliding_file_name(self._media_url)
            + ".jpg"
        )
        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                self._media_url,
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

    @log_function_params
    def get_last_frame_as_image(self):
        """
        Get the last frame of the video
        """
        assert self._media_url, "no media URL provided"
        assert os.path.exists(self._media_url), "The video file does not exist"
        result_path = (
            "last_frame_video_"
            + osnamingtools.create_non_colliding_file_name(self._media_url)
            + ".jpg"
        )
        result = subprocess.run(
            [
                "ffmpeg",
                "-sseof",  # spécifie qu'il doit commencer à x secondes de la fin du fichier.
                "-3",  # on veut les 3 dernières secondes
                "-i",
                self._media_url,
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
            if self._media_url is None:
                raise ValueError("The source media URL is not set")
            self._duration = float(get_media_duration(self._media_url))
        return self._duration

    @log_function_params
    def _apply_background_music(self, background_music_file: str = None):
        """
        Set the background music for the current video

        Currently we just add a single music background of the length of the final video

        Args:
            background_music (str): The path to the background music file
        Returns:
            The current instance of the video
        """
        if background_music_file:
            self._background_music_file_name = background_music_file  # Note that here we might overwrite the existing background music file
            assert os.path.exists(
                self._background_music_file_name
            ), f"File {self._background_music_file_name} does not exist"

        self._media_url = merge_audio(
            media_url=self.media_url, audio_file_path=self._background_music_file_name
        )
        return self

    def _apply_subtitle(self, build_settings: VideoBuildSettings):
        if build_settings.prompt is RecordedPrompt:
            if build_settings.prompt.audio_recording:
                merge_audio(
                    media_url=self._media_url,
                    prompt=build_settings.prompt.audio_recording,
                )

    @abstractmethod
    def build(self, build_settings: VideoBuildSettings = None):
        """
        Build the video in the child classes, unless the video is already built, in  which case
        we just return ourseleves (Video gets immutable once generated)

        Args:
            build_settings (VideoBuildSettings): The settings to use for building the video

        Returns:
            Video: The built video

        """
        if self._is_video_generated:
            return self

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

    def _build_background_music(
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
            self._background_music_file_name = self._generate_music(
                expected_music_length=self.get_duration(),
                test_mode=build_settings.test_mode,
                prompt_text=prompt_text,
            )
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

    def _generate_music(
        self,
        expected_music_length,
        prompt_text: str = None,
        test_mode: bool = True,
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

        ml_models_gateway = (
            ML_models_gateway_factory.MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=test_mode
            )
        )

        return ml_models_gateway.generate_background_music(
            duration=expected_music_length, prompt=prompt_text
        )
