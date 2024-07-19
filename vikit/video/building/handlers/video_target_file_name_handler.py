import shutil
import os

from loguru import logger
from vikit.video.building import video_building_handler
from vikit.video.video import Video
from vikit.common.file_tools import get_path_type, is_valid_path


class VideoBuildingHandlerTargetFileSetter(video_building_handler.VideoBuildingHandler):
    def __init__(self, **kwargs):
        super().__init__(kwargs=kwargs)
        self._target_file_name = None

        if "video_target_path" in kwargs:
            self._target_file_name = kwargs["video_target_file_name"]
        else:
            raise ValueError("Video target file name is required")

        if "video_target_path" in kwargs:
            self._target_dir_path = kwargs["video_target_dir_path"]
        else:
            raise ValueError("video_target_path file name is required")

    def is_supporting_async_mode(self):
        return True

    async def _execute_logic_async(self, video: Video, **kwargs):
        await super()._execute_logic_async(video)
        """
        Rename the video media file to the target file name if not already set
        to the target file name. 
        Todday this function only works for local files.
        We fail open: in case no target file name works, we just keep the video 
        as it is and where it stands. We send a warning to the logger though.

        Args:
            video (Video): The video to process

        Returns:
            The video with the target file name
        """
        continue_processing = True
        if not self._target_file_name:
            if is_valid_path(video.video.build_settings.target_file_name):
                logger.warning(
                    f"Video target file name is not set. Using the one from the video build settings"
                )
                logger.debug(
                    f"Video target file name from build settings: {video.build_settings.target_file_name}"
                )
                self._target_file_name = video.build_settings.output_file_name
            else:
                logger.warning(
                    "Video target file name is None or invalid, using the video as it is"
                )
                continue_processing = False
        else:
            if not is_valid_path(self._target_file_name):
                logger.warning(
                    "Video target file name is None or invalid, using the video as it is"
                )
                continue_processing = False

        if continue_processing:
            # Rename the video media file to the target file name
            if get_path_type(video.media_url)["type"] == "local":
                dir_name = os.path.dirname(self._target_file_name)
                file_name = os.path.basename(video.media_url)
                if (
                    dir_name != self._target_file_name
                    or file_name != self._target_dir_path
                ):
                    if not os.path.exists(dir_name):
                        os.makedirs(dir_name)
                    logger.debug(
                        f"Copying video media file from {video.media_url} to {self._target_file_name}"
                    )
                    assert os.path.exists(
                        video.media_url
                    ), f"File not found: {video.media_url}"
                    shutil.copyfile(
                        video.media_url,
                        os.path.join(self._target_dir_path, self._target_file_name),
                    )
                    video.media_url = self._target_file_name
            else:
                logger.warning(
                    f"Video media url is not local: {video.media_url}. Cannot rename to target file name yet"
                )

        return video, kwargs

    def _execute_logic(self, video: Video, **kwargs) -> Video:
        """
        Process the video generation  synchronously
        """
        pass
