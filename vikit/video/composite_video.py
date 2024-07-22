import os
import random
import shutil
import uuid as uid

from loguru import logger
from vikit.video.video import Video
from vikit.video.video_build_settings import VideoBuildSettings
import vikit.common.config as config

from vikit.video.video_types import VideoType
from vikit.video.building.build_order import (
    get_lazy_dependency_chain_build_order,
    is_composite_video,
)
from vikit.music_building_context import MusicBuildingContext
from vikit.wrappers.ffmpeg_wrapper import concatenate_videos
from vikit.video.building.handlers.video_reencoding_handler import (
    VideoReencodingHandler,
)
from vikit.common.handler import Handler
from vikit.common.file_tools import get_path_type


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

        self._is_root_video_composite = True  # true until we have a composite video that will add this composite as a child using append
        self.video_list = []

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

    def get_cascaded_build_settings(self):
        """
        Get the cascaded build settings
        """
        return VideoBuildSettings(
            interpolate=self.build_settings.interpolate,
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
        self.video_list.append(video)

        if (
            video._needs_video_reencoding
        ):  # Adding a video that needs reencoding will trigger reencoding of the whole tree
            self._needs_video_reencoding = True

        if type(video) is CompositeVideo:
            logger.debug(
                f"Added composite video {video.id} to composite video {self.id}"
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
            # TODO: handle partially interpolated videos, not really importnat for now

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

    async def prepare_build_hook(self, build_settings: VideoBuildSettings):
        """
        Prepare the video before launching the video build process:

        here we ensure child videos won't have buildsettings with music, etc
        unless they would already have been prepared with sepecific build settings

        Args:
            build_settings (VideoBuildSettings): The build settings

        Returns:
            list: The video build order
        """
        self.build_settings = build_settings
        for video in self.video_list:
            if not video.are_build_settings_prepared:
                await video.prepare_build_hook(
                    build_settings=self.get_cascaded_build_settings()
                )

        # Cleanse the video list by removing any empty composites videos
        self.video_list = self.cleanse_video_list()
        self.are_build_settings_prepared = True

        return self

    async def run_build_core_logic_hook(
        self,
        build_settings=VideoBuildSettings(),
    ):
        """
        Mix all the videos in the list: here we actually build and stitch the videos together, will take some time and resources,
        as we call external services and run video mixing locally.

        params:
            build_settings: The settings to be used for the build

        Returns:
            self: The current object
        """
        if (
            self._is_root_video_composite
        ):  # This check is important: we generate an ordered video list
            # for the whole video tree at once
            ordered_video_list = get_lazy_dependency_chain_build_order(
                video_tree=self.video_list,
                build_settings=build_settings,
                already_added=set(),
            )
            for video in ordered_video_list:
                await video.build(build_settings=build_settings)

        self.media_url = await self.concatenate()

        return self

    async def concatenate(self):
        """
        Concatenate the videos for this composite
        """

        short_title = self.get_title()
        # TODO: change this hard truncate!!
        if len(short_title) > 20:
            logger.warning(
                f"Video title is too long: {short_title}, truncating to 20 characters, new title: {short_title[:20]}"
            )
            short_title = short_title[:20]

        video_list_file = "_".join(
            [
                short_title,
                str(random.getrandbits(16)),
                config.get_video_list_file_name(),
            ]
        )
        ratio = self._get_ratio_to_multiply_animations(
            build_settings=self.build_settings
        )
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

    def _get_ratio_to_multiply_animations(self, build_settings: VideoBuildSettings):
        # Now we box the video composing this composite into the expected length, typically the one of a prompt
        if build_settings.expected_length is None:
            if build_settings.prompt is not None:
                logger.debug(
                    f"parameters video_composite.get_duration() build_settings.prompt : {self.get_duration()}, {build_settings.prompt}"
                )
                ratioToMultiplyAnimations = (
                    self.get_duration() / build_settings.prompt.duration
                )
            else:
                ratioToMultiplyAnimations = 1
        else:
            if build_settings.expected_length <= 0:
                raise ValueError(
                    f"Expected length should be greater than 0. Got {build_settings.expected_length}"
                )
            ratioToMultiplyAnimations = (
                self.get_duration() / build_settings.expected_length
            )

        return ratioToMultiplyAnimations

    async def run_post_build_actions_hook(self, build_settings: VideoBuildSettings):
        if not build_settings.output_file_name:
            name, extension = os.path.splitext(os.path.basename(self.media_url))
            new_name = f"{name}_{uid.uuid4()}{extension}"
            build_settings.output_file_name = os.path.join(
                os.path.dirname(self.media_url), new_name
            )
            logger.warning(
                f"Output file name not set, using a random name: {build_settings.output_file_name}"
            )

        if self._is_root_video_composite:
            self.set_final_video_name(
                target_dir_path=build_settings.output_path,
                output_file_name=build_settings.output_file_name,
            )

    def set_final_video_name(self, target_dir_path: str, output_file_name: str):
        """
        Rename the video media file to the target file name if not already set
        to the target file name.
        Todday this function only works for local files.
        We fail open: in case no target file name works, we just keep the video
        as it is and where it stands. We send a warning to the logger though.

        Args:
            target_file_path (str): The target file path
            output_file_name (str): The output file name

        Returns:
            The video with the target file name
        """
        # Rename the video media file to the target file name
        if not target_dir_path or get_path_type(target_dir_path)["type"] == "local":
            current_dir_name = os.path.dirname(self.media_url)
            current_file_name = os.path.basename(self.media_url)
            if (
                current_dir_name != target_dir_path
                or current_file_name != output_file_name
            ):
                new_file_path = (
                    output_file_name
                    if not target_dir_path
                    else os.path.join(target_dir_path, output_file_name)
                )
                logger.debug(
                    f"Copying video media file from {self.media_url} to {new_file_path}"
                )
                if target_dir_path:
                    assert os.path.exists(
                        target_dir_path
                    ), f"File {target_dir_path} does not exist"

                shutil.copyfile(
                    self.media_url,
                    new_file_path,
                )
                self.media_url = new_file_path
        else:
            raise ValueError(
                f"Target dir path is not local: {target_dir_path}. Cannot rename to target file name yet"
            )

    def generate_background_music_prompt(self):
        """
        Get the background music prompt from the video list.

        returns:
            str: The background music prompt
        """
        return " ".join(
            [video.get_title() for video in self.video_list if video.get_title()]
        )

    def get_core_handlers(self, build_settings) -> list[Handler]:
        """
         Get the handler chain of the video. Order matters here.

        Args:
             build_settings (VideoBuildSettings): The settings for building the video

         Returns:
             list: The list of handlers to use for building the video
        """
        handlers = []

        if (
            len(
                list(
                    filter(lambda video: video._needs_video_reencoding, self.video_list)
                )
            )
            >= 1
        ):
            handlers.append(VideoReencodingHandler())
            logger.debug(
                f"Added video reencoding handler for composite video {self.id}"
            )

        return handlers
