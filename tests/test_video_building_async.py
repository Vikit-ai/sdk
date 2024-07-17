import pytest

import warnings
from loguru import logger

from vikit.common.decorators import log_function_params
import tests.tests_medias as test_media
from vikit.video.video import VideoBuildSettings
from vikit.common.context_managers import WorkingFolderContext
from vikit.video.raw_text_based_video import RawTextBasedVideo
import tests.tests_tools as tools
from vikit.wrappers.ffmpeg_wrapper import get_media_duration
from vikit.music_building_context import MusicBuildingContext

prompt_mystic = tools.test_prompt_library["moss_stones-train_boy"]


class TestVideoBuildingAsync:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        warnings.simplefilter("ignore", category=DeprecationWarning)
        logger.add("log_test_video.txt", rotation="10 MB")
        self.sample_cat_video_path = test_media.get_cat_video_path()
        self.prompt_loosing_faith = None
        logger.add("log_test_composite_video.txt", rotation="10 MB")

    @pytest.mark.local_integration
    @log_function_params
    async def test_generate_bg_music_async(self):
        with WorkingFolderContext():
            video = RawTextBasedVideo(prompt_mystic.text)
            video.media_url = self.sample_cat_video_path
            bg_music_file = video._build_background_music(
                build_settings=VideoBuildSettings(
                    test_mode=True,
                    music_building_context=MusicBuildingContext(
                        generate_background_music=True,
                        apply_background_music=True,
                    ),
                ),
                prompt_text="mystic space interstellar electronic",
            )

            assert bg_music_file is not None
            assert get_media_duration(bg_music_file) > 0

    @pytest.mark.local_integration
    @pytest.mark.skip(reason="Test is not yet implemented")
    @log_function_params
    async def test_generate_video_async(self):
        with WorkingFolderContext():
            video = RawTextBasedVideo(prompt_mystic.text)
            await video.build(
                build_settings=VideoBuildSettings(
                    test_mode=True,
                    music_building_context=MusicBuildingContext(
                        apply_background_music=False,
                    ),
                )
            )

            assert video is not None
            assert get_media_duration(video.media_url) > 0
