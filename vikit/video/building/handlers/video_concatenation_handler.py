import os

from vikit.video.building import video_building_handler
from vikit.video.video import Video
from vikit.wrappers.ffmpeg_wrapper import concatenate_videos


class VideoBuildingHandlerConcatenate(video_building_handler.VideoBuildingHandler):
    def __init__(self, **kwargs):
        super().__init__()
        if "video_list_file" not in kwargs:
            raise ValueError("video_list_file must be provided")
        self.video_list_file_path = kwargs["video_list_file"]

    def is_supporting_async(self):
        return True

    def _execute_logic_async(self, video: Video, **kwargs):
        """
        Execute the handler asynchronously: Concatenate videos
        listed into a file to create a new video, using FFMPEG
        """
        # Precondition: need to woek on a composite video
        if not video.is_composite:
            raise ValueError("Video must be a composite video to be concatenated")

        super()._execute_logic_async(video=video, kwargs=kwargs)
        ratio = self._get_ratio_to_multiply_animations(
            build_settings=video.build_settings, video_composite=video
        )
        # We have the final file names (they may have changed between initial video instanciation and
        # inference of a name after querying an LLM
        video_list_file = self.video_list_file_path
        with open(video_list_file, "w") as myfile:
            for video in self.video_list:
                file_name = video.media_url
                myfile.write("file " + file_name + os.linesep)

        self._media_url = concatenate_videos(
            input_file=os.path.abspath(video_list_file),
            target_file_name=video_building_handler.get_file_name_by_state(
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

    def _execute_logic(self, video: Video, **kwargs):
        return super()._execute_logic(video=video, kwargs=kwargs)
