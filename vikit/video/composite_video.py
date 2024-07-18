import os
import uuid

from loguru import logger
from vikit.video.video import Video
from vikit.video.video_build_settings import VideoBuildSettings
from vikit.common.decorators import log_function_params
import vikit.common.config as config

from vikit.video.video_types import VideoType
from vikit.video.building.build_order import (
    get_lazy_dependency_chain_build_order,
    is_composite_video,
)
from vikit.music_building_context import MusicBuildingContext
from vikit.wrappers.ffmpeg_wrapper import concatenate_videos, merge_audio
from vikit.video.building.video_building_handler import VideoBuildingHandler
from vikit.video.building.handlers.video_target_file_name_handler import (
    VideoBuildingHandlerTargetFileSetter,
)
from vikit.video.building.handlers.default_bg_music_and_audio_merging_handler import (
    DefaultBGMusicAndAudioMergingHandler,
)
from vikit.video.building.handlers.use_prompt_audio_track_and_audio_merging_handler import (
    UsePromptAudioTrackAndAudioMergingHandler,
)
from vikit.video.building.handlers.gen_read_aloud_prompt_and_audio_merging_handler import (
    ReadAloudPromptAudioMergingHandler,
)
from vikit.video.building.handlers.gen_music_and_audio_merging_handler import (
    VideoMusicBuildingHandlerGenerateFomApi,
)
from vikit.video.building.handlers.video_reencoding_handler import (
    VideoReencodingHandler,
)

# from vikit.video.building.handlers.interpolation_handler import (
#     VideoBuildingHandlerInterpolate,
# )


class CompositeVideo(Video, is_composite_video):
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
        self._initialized_video_handler_chain = None

    def is_composite_video(self):
        return True

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

    def get_cascaded_build_settings(self):
        """
        Get the cascaded build settings
        """
        return VideoBuildSettings(
            interpolate=True,
            run_async=self.build_settings.run_async,
            include_read_aloud_prompt=False,
            music_building_context=MusicBuildingContext(apply_background_music=False),
            test_mode=self.build_settings.test_mode,
        )

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
        video_type = (
            str(VideoType.COMPROOT)
            if self._is_root_video_composite
            else str(VideoType.COMPCHILD)
        )

        return str(
            super().get_file_name_by_state(
                build_settings=build_settings,
                video_type=video_type,
                metadata=self.metadata,
            )
        )

    def update_metadata_post_building(self):
        """
        Update the metadata post building
        """
        self._is_video_generated = True

        nb_interpolated = len(
            list(
                filter(
                    lambda builtvideo: builtvideo.metadata.is_interpolated,
                    self._video_list,
                )
            )
        )
        if nb_interpolated < len(self._video_list):
            self.metadata.is_interpolated
        elif nb_interpolated == 0:
            self.metadata.is_interpolated = False
            # TODO: handle partially interpolated videos, not really importnat for now

    def cleanse_video_list(self):
        """
        Cleanse the video list by removing any empty composites videos
        """
        return list(
            filter(
                lambda video: not (
                    isinstance(video, CompositeVideo) and len(video._video_list) == 0
                ),
                self._video_list,
            )
        )

    async def prepare_build(self, build_settings: VideoBuildSettings):
        """
        Prepare the video before launching the video build process:

        - ensure the buildsettings are tight to the corresponding videos
        - Prepare the video build order list and initialize it

        Args:
            build_settings (VideoBuildSettings): The build settings
            strategy (str): the function to use to generate the video build order list

        Returns:
            list: The video build order
        """
        await super().prepare_build(build_settings=build_settings)
        assert self.build_settings is not None, "Build settings should be provided"
        for video in self.video_list:
            if not video.are_build_settings_prepared:
                await video.prepare_build(
                    build_settings=self.get_cascaded_build_settings()
                )

        return self

    @log_function_params
    async def build(
        self,
        build_settings=VideoBuildSettings(),
    ):
        """
        Mix all the videos in the list: here we actually build and stitch the videos together, will take some time and resources,
        as we call external services and run video mixing locally.

        params:
            build_settings: The settings to be used for the build
            build_order: The order in which to build the videos

        Returns:
            self: The current object
        """
        if self._is_video_generated:
            return self

        await self.prepare_build(build_settings=build_settings)
        if self._is_root_video_composite:
            # Cleanse the video list by removing any empty composites videos
            self._video_list = self.cleanse_video_list()

            # The list below is generated in a control and command way,
            # i.e. for the whole tree of composites, we generate the list of videos to be built
            ordered_video_list = get_lazy_dependency_chain_build_order(
                video_tree=self.video_list,
                build_settings=build_settings,
                already_added=set(),
            )
            logger.debug(
                f"Ordered video list for composite {self.get_title()}: {ordered_video_list}"
            )
            for video in ordered_video_list:
                await video.build(build_settings=build_settings)

        self.media_url = await self.concatenate()
        for handler in self.get_and_initialize_video_handler_chain(
            build_settings=build_settings
        ):
            if handler.is_supporting_async_mode():
                built_video, _ = await handler.execute_async(video=self)
            else:
                built_video = handler.execute(video=self)

        self.run_post_build_actions()

        return self

    async def concatenate(self):
        """
        Concatenate the videos in the list

        Args:
            video_list_file (str): The video list file
            short_title (str): The short title
        """

        short_title = self.get_title()
        # TODO: change this hard truncate!!
        if len(short_title) > 20:
            short_title = short_title[:20]

        video_list_file = "_".join(
            [
                short_title,
                config.get_video_list_file_name(),
            ]
        )
        ratio = self._get_ratio_to_multiply_animations(
            build_settings=self.build_settings, video_composite=self
        )

        # We have the final file names (they may have changed between initial video instanciation and
        # inference of a name after querying an LLM
        # In a future version, the ordering of concatenations may vary to accelerate the
        # production of composites before others, to start the first one asap
        with open(video_list_file, "w") as myfile:
            for video in self.video_list:
                file_name = video.media_url
                myfile.write("file " + file_name + os.linesep)

        return await concatenate_videos(
            input_file=os.path.abspath(video_list_file),
            target_file_name=self.get_file_name_by_state(
                build_settings=video.build_settings,
            ),
            ratioToMultiplyAnimations=ratio,
        )  # keeping one consistent file name

    def _get_ratio_to_multiply_animations(self, build_settings, video_composite):
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

    @log_function_params
    async def _insert_subtitles_audio_recording(
        self, build_settings: VideoBuildSettings
    ):
        """
        Insert the subtitles audio recording
        """
        bld_set_interim = build_settings
        bld_set_interim.include_read_aloud_prompt = True
        self.metadata.is_prompt_read_aloud = True

        if build_settings.prompt:
            self._media_url = await merge_audio(
                media_url=self.media_url,
                audio_file_path=build_settings.prompt._recorded_audio_prompt_path,
                target_file_name=self.get_file_name_by_state(bld_set_interim),
            )
            self.metadata.is_subtitle_audio_applied = True
        else:
            logger.warning("No prompt audio file provided, skipping audio insertion")

    @log_function_params
    def generate_background_music_prompt(self):
        """
        Get the background music prompt from the video list.

        returns:
            str: The background music prompt
        """
        return " ".join(
            [video.get_title() for video in self.video_list if video.get_title()]
        )

    def get_and_initialize_video_handler_chain(
        self, build_settings: VideoBuildSettings
    ) -> list[VideoBuildingHandler]:
        """
        Get the handler chain of the video.
        Defining the handler chain is the main way to define how the video is built
        so it is up to the child classes to implement this method

        Args:
            build_settings (VideoBuildSettings): The settings to use for building the video

        Returns:
            list: The list of handlers to use for building the video
        """
        handlers = []
        # Directly going to post video building handlers as we are in a composite
        # Interpolating a composite may be experimented later
        # if self.interpolate:
        #     handlers.append(VideoBuildingHandlerInterpolate())
        if self._needs_reencoding:
            handlers.append(VideoReencodingHandler())

        # You may use specific background music and prompt audio for the composite video
        # even if not a root composite, in case the composite is a part of a bigger video
        # and if you think it is long enough to add them
        if build_settings.music_building_context.apply_background_music:
            if build_settings.music_building_context.generate_background_music:
                bg_music_prompt = self.generate_background_music_prompt()
                if not bg_music_prompt or bg_music_prompt == "":
                    logger.warning(
                        "No prompt provided for background music generation, using the prompt full text to inspire the music"
                    )
                    bg_music_prompt = build_settings.prompt.full_text
                music_file_name = f"generated_music_uid_{str(uuid.uuid4())}.mp3"
                handlers.append(
                    VideoMusicBuildingHandlerGenerateFomApi(
                        target_music_file_name=music_file_name,
                        bg_music_prompt=bg_music_prompt,
                        duration=(
                            build_settings.music_building_context.expected_music_length
                            if build_settings.music_building_context.expected_music_length
                            else build_settings.prompt.get_duration()
                        ),
                    )
                )
            else:
                if build_settings.music_building_context.use_recorded_prompt_as_audio:
                    handlers.append(UsePromptAudioTrackAndAudioMergingHandler())
                else:
                    handlers.append(DefaultBGMusicAndAudioMergingHandler())

        if build_settings.include_read_aloud_prompt:
            if build_settings.prompt:
                handlers.append(
                    ReadAloudPromptAudioMergingHandler(
                        audio_file=build_settings.prompt._recorded_audio_prompt_path
                    )
                )
            else:
                logger.warning(
                    "No prompt audio file provided, skipping audio insertion"
                )

        if (
            self._is_root_video_composite
        ):  # set the target file name only for the final root composite
            if build_settings._output_path:
                handlers.append(
                    VideoBuildingHandlerTargetFileSetter(
                        video_target_file_name=self.build_settings._output_path
                    )
                )

        return handlers
