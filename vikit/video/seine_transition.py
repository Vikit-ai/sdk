from loguru import logger
from urllib.request import urlretrieve

from vikit.video.video import Video, VideoBuildSettings

import vikit.gateways.ML_models_gateway_factory as ML_models_gateway_factory
from vikit.common.decorators import log_function_params
from vikit.video.transition import Transition, url_exists


class SeineTransition(Transition):

    def __init__(
        self,
        source_video: Video,
        target_video: Video,
    ):
        """
        A Seine transition is a video that is generated between two videos
        """
        super().__init__(source_video=source_video, target_video=target_video)

    def _infer_video_path(self):
        """
        Infer the path to the transition video
        """
        return (
            "transition_[seine]_from_"
            + self._source_video.get_title()
            + "_to_"
            + self._target_video.get_title()
            + ".mp4"
        )

    @log_function_params
    def build(self, build_settings: VideoBuildSettings = None) -> Transition:
        """
        Apply the Seine transition between the source and target video

        Args:
            build_settings (VideoBuildSettings): The settings for building the video

        Returns:
            str: The path to the generated transition video
        """
        super().build(build_settings)

        if self._is_video_generated:
            return self

        if not self._source_video._is_video_generated:
            self._source_video.build(build_settings=build_settings)
        if not self._target_video._is_video_generated:
            self._target_video.build(build_settings=build_settings)

        assert self._source_video._is_video_generated, "source video must be generated"
        assert self._target_video._is_video_generated, "target video must be generated"
        assert url_exists(self._source_video.media_url), "source_video must exist"
        assert url_exists(self._target_video.media_url), "target_video must exist"

        logger.debug(
            f"Applying transition from {self._source_video.media_url} to {self._target_video.media_url}"
        )
        ml_gw = build_settings.get_ml_models_gateway()
        # We generate a transition
        link_to_transition_video = ml_gw.generate_seine_transition(
            source_image_path=self._source_video.get_last_frame_as_image(),
            target_image_path=self._target_video.get_first_frame_as_image(),
        )
        print("Link to transition video " + link_to_transition_video)
        logger.debug(
            f"URL Retrieved to be quality augmented {link_to_transition_video}"
        )
        interpolated_transition_link = ml_gw.interpolate(link_to_transition_video)
        # Then we download it
        target_file_name = self._infer_video_path()
        urlretrieve(interpolated_transition_link, target_file_name)
        self._media_url = target_file_name

        return self
