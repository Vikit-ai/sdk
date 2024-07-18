import os

from loguru import logger
from vikit.common.decorators import log_function_params
from vikit.video.building import video_building_handler
from vikit.video.video import Video
from vikit.common.file_tools import get_validated_path


class VideoBuildingHandlerTargetFileSetter(video_building_handler.VideoBuildingHandler):
    def __init__(self, **kwargs):
        super().__init__(kwargs=kwargs)
        if "video_target_file_name" in kwargs:
            self._target_file_name = kwargs["video_target_file_name"]
        else:
            raise ValueError("Video target file name is required")

    def is_supporting_async_mode(self):
        return True

    @log_function_params
    async def _execute_logic_async(self, video: Video, **kwargs):
        await super()._execute_logic_async(video)
        """
        Rename the video media file to the target file name if not already set
        to the target file name. 
        Todday this function only works for local files.

        Args:
            video (Video): The video to process

        Returns:
            The video with the target file name
        """
        await super()._execute_logic_async(video, **kwargs)
        if video.media_url != self._target_file_name:
            # Rename the video media file to the target file name
            path = get_validated_path(video.media_url)
            if path["is_local"]:
                # Copy the file to the target file name using os.rename
                os.rename(video.media_url, self._target_file_name)
            else:
                logger.warning(
                    f"Video media url is not local: {video.media_url}. Cannot rename to target file name"
                )
            video.media_url = self._target_file_name

        return video, kwargs

    def _execute_logic(self, video: Video, **kwargs) -> Video:
        """
        Process the video generation  synchronously
        """
        pass
