import os

from loguru import logger

from vikit.video.video import Video, VideoBuildSettings
from vikit.common.decorators import log_function_params
from vikit.wrappers.ffmpeg_wrapper import merge_audio
from vikit.music import MusicBuildingContext
from vikit.video.composite_video_builder_strategy_factory import (
    CompositeVideoBuilderStrategyFactory,
)
from vikit.video.composite_video_builder_strategy import CompositeVideoBuilderStrategy
from vikit.video.video_file_name import VideoFileName
from vikit.video.video_types import VideoType


class CompositeVideo(Video):
    """
    Composite made from the collection of videos that need to be generated altogether, as a consistent block
    It could be a final video or intermediate  composing specific scenes of the final video.

    Composite video can include other composite videos, and so on, to build a tree of videos to be generated
    """

    def __init__(self, target_file_name=None):
        """
        We can initialize a VideoComposite using a subtitle to work on it
        and help set the right length for the appended videos or video composites
        and to be generated as a single block
        """
        super().__init__()

        if target_file_name is not None:
            if not target_file_name.endswith(".mp4"):
                raise ValueError("The target file name should end with .mp4")
            self._media_url = target_file_name
        else:
            self._media_url = type(self).__name__ + ".mp4"

        self._background_music_file_name = None
        self._is_video_generated = False
        self._is_root_video_composite = True  # true until we have a composite video that will add this composite as a child using append
        self._title = None
        self._video_list = []
        self._needs_reencoding = (
            False  # Maybe used for composite containing imported videos
        )
        self._is_video_generated = False
        self._parent = None  # The parent video composite, helpfull for some optimisations like cascading up
        # the fact to know we have an imported video somewhere and trigger reecoding of the whole tree
        self._video_file_name = None

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        if self._is_root_video_composite:
            return str(VideoType.COMPROOT)
        else:
            return str(VideoType.COMPCHILD)

    @property
    def video_list(self) -> list[Video]:
        return self._video_list

    def __str__(self):
        videos_output = (
            super().__str__() + os.linesep + "----- Composite video video list-----"
        )
        for video in self._video_list:
            videos_output = videos_output + "ID: " + video.id + os.linesep

        return f"Composite Video: {videos_output}"

    @log_function_params
    def append_video(self, video: Video = None):
        """
        Append a video to the list of videos to be mixed

        params:
            video: The video to be appended

        returns:
            self: The current object
        """
        if video is None:
            raise ValueError("video cannot be None")
        video.top_parent_id = self.top_parent_id  # We cascade the top parent id
        self._video_list.append(video)

        if (
            video._needs_reencoding
        ):  # Adding a video that needs reencoding will trigger reencoding of the whole tree
            self._needs_reencoding = True

        if type(video) is CompositeVideo:
            video._is_root_video_composite = False
            video.metadata.top_parent_id = self.top_parent_id

        return self

    def get_duration(self):
        """
        Get the duration of the video, we recompute it everytime
        as the duration of the video can change if we add or remove videos
        """
        all_video_duration = 0
        for video in self.video_list:
            all_video_duration += video.get_duration()
        self._duration = all_video_duration

        self.metadata.duration = all_video_duration
        return all_video_duration

    def get_title(self):
        """
        Get the title of the video, we recompute it everytime
        as the title of the video can change if we add or remove videos
        """
        title = "_".join([subvideo.get_title() for subvideo in self.video_list])
        self._title = "empty-composite" if title == "" else title

        self.metadata.title = self._title
        return self._title

    @log_function_params
    def get_file_name_by_state(self, build_settings: VideoBuildSettings = None):
        """
        Get the target / expected file name for the composite video depending on its state
        State is build progressively from Instantiation to the final build, where steps like
        adding music or audio prompt are carried out

        params:
            build_settings: The settings to be used for the build

        returns:
            str: The target file name
        """
        if build_settings is None:
            raise ValueError("build_settings cannot be None")

        video_type = (
            str(VideoType.COMPROOT)
            if self._is_root_video_composite
            else str(VideoType.COMPCHILD)
        )
        video_fname = super().get_file_name_by_state(
            build_settings=build_settings, video_type=video_type
        )
        return str(video_fname)

    @log_function_params
    def build(
        self,
        build_settings=VideoBuildSettings(),
        building_strategy: CompositeVideoBuilderStrategy = None,
    ):
        """
        Mix all the videos in the list: here we actually build and stitch the videos together, will take some time and resources,
        as we call external services and run video mixing locally.

        The actual algorithm depends on the provided strategy (local, cloud, etc.)

        :param build_settings: The settings to be used for the build
        :param building_strategy: The strategy to be used for the build

        Returns:
            self: The current object
        """
        super().build(build_settings)

        if self._is_video_generated:
            return self

        # Cleanse the video list by removing any empty composites videos
        self._video_list = list(
            filter(
                lambda video: not (
                    isinstance(video, CompositeVideo) and len(video._video_list) == 0
                ),
                self._video_list,
            )
        )

        if building_strategy is None:  # Fail open, take the local strategy
            building_strategy = (
                CompositeVideoBuilderStrategyFactory().get_local_building_strategy()
            )
        else:
            building_strategy = building_strategy

        generated_vid_composite = building_strategy.execute(
            composite_video=self, build_settings=build_settings
        )

        if self._is_root_video_composite:
            # Handle the background music
            if build_settings.music_building_context.apply_background_music:
                if build_settings.music_building_context.use_recorded_prompt_as_audio:
                    generated_vid_composite._apply_background_music(
                        build_settings.prompt.audio_recording
                    )
                else:  # we generate the background music (either trough a model or use a default music to fail open)
                    music_file = super()._build_background_music(
                        prompt_text=generated_vid_composite._generate_background_music_prompt(),
                        build_settings=VideoBuildSettings(
                            test_mode=build_settings.test_mode,
                            music_building_context=MusicBuildingContext(
                                generate_background_music=build_settings.music_building_context.generate_background_music,
                                expected_music_length=(
                                    build_settings.prompt.get_duration()
                                    if build_settings.prompt is not None
                                    else None
                                ),
                            ),
                        ),
                    )

                    generated_vid_composite._apply_background_music(music_file)

            # Insert the subtitles audio recording
            if build_settings.include_audio_subtitles:
                generated_vid_composite._insert_subtitles_audio_recording(
                    build_settings
                )

        self.metadata.is_video_generated = True

        return generated_vid_composite

    @log_function_params
    def _insert_subtitles_audio_recording(self, build_settings: VideoBuildSettings):
        """
        Insert the subtitles audio recording
        """
        bld_set_interim = build_settings
        bld_set_interim.include_audio_subtitles = True
        self.metadata.is_prompt_read_aloud = True

        if build_settings.prompt:
            self._media_url = merge_audio(
                media_url=self.media_url,
                audio_file_path=build_settings.prompt._recorded_audio_prompt_path,
                target_file_name=self.get_file_name_by_state(bld_set_interim),
            )

        else:
            logger.warning("No prompt audio file provided, skipping audio insertion")

        self.metadata.is_subtitle_audio_applied = True

    @log_function_params
    def _generate_background_music_prompt(self):
        """
        Get the background music prompt from the video list.

        returns:
            str: The background music prompt
        """
        return " ".join(
            [video.get_title() for video in self.video_list if video.get_title()]
        )
