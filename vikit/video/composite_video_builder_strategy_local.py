import random
from concurrent.futures import ProcessPoolExecutor
import os

# import atexit

from loguru import logger

from vikit.video.video_build_settings import VideoBuildSettings
import vikit.common.config as config
from vikit.wrappers.ffmpeg_wrapper import concatenate_videos, reencode_video
from vikit.video.composite_video_builder_strategy import (
    CompositeVideoBuilderStrategy,
)

# # The following code is used to mutualize the processexecutor across all the CompositeVideoBuilderStrategyLocal instances
executor = ProcessPoolExecutor()


# def shutdown_executor():
#     executor.shutdown(wait=True)


# atexit.register(shutdown_executor)


class CompositeVideoBuilderStrategyLocal(CompositeVideoBuilderStrategy):
    """
    Composite video builder strategy local is the strategy to build composite videos locally:

    - call API's to generate the videos and transitions
    - call ffmpeg to concatenate the videos locally using your computer resources

    """

    def execute(
        self, composite_video: "CompositeVideo", build_settings: VideoBuildSettings
    ) -> "CompositeVideo":
        """
        Mix all the videos in the list: here we actually build and stitch the videos together, will take some time and resources,
        as we call external services and run video mixing locally.
        The video mixing process happens once we have all the videos to mix

        Args:
            composite_video: The composite video
            build_settings: The build settings

        Returns:
            CompositeVideo: The composite video
        """
        if composite_video is None:
            raise ValueError("Composite video cannot be None")
        self._composite_video = composite_video

        short_title = composite_video.get_title()
        if len(short_title) > 20:
            short_title = short_title[:20]

        video_list_file = "_".join(
            [
                short_title,
                config.get_video_list_file_name(),
            ]
        )

        cascaded_build_settings = VideoBuildSettings(  # we will handle the background only at the video composite root level
            include_audio_read_subtitles=False,  # we will handle the subtitles only at the video composite root level
            test_mode=build_settings.test_mode,
            run_async=build_settings.run_async,
        )

        # Generate the videos
        self._composite_video._video_list = self.process_videos_async(
            build_settings=cascaded_build_settings,
            video_list=self._composite_video.video_list,
            function_to_invoke=self._process_gen_vid_bins,
        )
        nb_interpolated = len(
            list(
                filter(
                    lambda builtvideo: builtvideo.metadata.is_interpolated,
                    self._composite_video._video_list,
                )
            )
        )

        if nb_interpolated < len(self._composite_video._video_list):
            self._composite_video.metadata.is_interpolated
        elif nb_interpolated == 0:
            self._composite_video.metadata.is_interpolated = False
        # else: #TODO: handle partially interpolated videos, not really importnat for now
        #     self.metadata.is_interpolated = True

        ratio = self._get_ratio_to_multiply_animations(
            build_settings=build_settings, video_composite=self._composite_video
        )
        if self._composite_video._needs_reencoding:
            self._composite_video._video_list = self.process_videos_async(
                build_settings=cascaded_build_settings,  # We take the freshly generated videos as input param
                video_list=self._composite_video.video_list,
                function_to_invoke=reencode_video,
            )
            self._composite_video.metadata.is_reencoded = True

        # We have the final file names (they may have changed between initial video instanciation and
        # inference of a name after querying an LLM
        with open(video_list_file, "w") as myfile:
            for video in self._composite_video.video_list:
                file_name = video._media_url
                myfile.write("file " + file_name + os.linesep)

        self._composite_video._media_url = concatenate_videos(
            input_file=os.path.abspath(video_list_file),
            target_file_name=self._composite_video.get_file_name_by_state(
                build_settings=build_settings
            ),
            ratioToMultiplyAnimations=ratio,
        )  # keeping one consistent file name

        self._composite_video._is_video_generated = True
        return self._composite_video

    def process_videos_async(
        self,
        build_settings: VideoBuildSettings,
        video_list,
        function_to_invoke,
    ):
        """
        Process the videos asynchronously

        Args:
            build_settings (VideoBuildSettings): The build settings
            video_list (list): The list of videos
            function_to_invoke (function): The function to invoke

        Returns:
            list: The list of processed videos
        """
        logger.debug(
            f"Processing videos asynchronously, run_async: {build_settings.run_async}"
        )

        if build_settings.run_async:
            logger.debug(
                f"Processing videos asynchronously, run_async: {build_settings.run_async}"
            )
            results = []
            for video in video_list:
                # TODO: you may have spotted that here we are not really processing the videos asynchronously, this caused some issues
                # for the 0.1 so we will imporve this in the next version, doing a map on the video_list
                results.extend(
                    executor.map(
                        function_to_invoke,
                        [(video, build_settings, video.media_url)],
                    )
                )
        else:
            logger.debug(
                f"Processing videos synchronously, run_async: {build_settings.run_async}"
            )
            results = []
            for video in video_list:
                results.extend(
                    [
                        function_to_invoke(
                            (
                                video,
                                build_settings,
                                video.media_url,
                                video.get_file_name_by_state(
                                    build_settings=build_settings
                                ),
                            )
                        )
                    ]
                )

        return results
