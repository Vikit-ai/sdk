from urllib.request import urlretrieve

from vikit.video.building import video_building_handler
from vikit.video.video import Video


class VideoBuildingHandlerTransitioni(video_building_handler.VideoBuildingHandler):
    def __init__(self):
        super().__init__()

    def is_supporting_async(self):
        return True

    async def _execute_logic_async(self, transition_video: Video, **kwargs) -> Video:
        super()._execute_logic_async(transition_video, kwargs=kwargs)
        """
        Process the video generation binaries: we actually do ask the video to build itself
        as a video binary (typically an MP4 generated from Gen AI, hosted behind an API),
        or to compose from its inner videos in case of a child composite video

        Args:
            args: The arguments: video, build_settings, video.media_url, target_file_name

        Returns:
            CompositeVideo: The composite video
        """
        super()._execute_logic_async(transition_video, **kwargs)

        video_link_from_prompt = await transition_video.build_settings.get_ml_models_gateway().generate_seine_transition_async(
            source_image_path=transition_video.source_video,
            target_image_path=transition_video.target_video,
        )

        file_name = self.get_file_name_by_state(transition_video.build_settings)
        transition_video.media_url = urlretrieve(
            video_link_from_prompt,
            (
                transition_video.build_settings.target_file_name
                if transition_video.build_settings.target_file_name
                else file_name
            ),
        )[0]

        return transition_video, kwargs

    def _execute_logic(self, video: Video, **kwargs) -> Video:
        """
        Process the video generation  synchronously
        """
        pass
