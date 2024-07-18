# This test suite is used to test the audio compositions that can be made on videos,
# like using background music, adding subtitles, etc.
# It does not map exactly to one single file to test


import warnings

import pytest
from loguru import logger

from tests.tests_medias import (
    get_cat_video_path,
    get_generated_3s_forest_video_1_path,
    get_generated_3s_forest_video_2_path,
)
from vikit.video.video import VideoBuildSettings
from vikit.video.imported_video import ImportedVideo
from vikit.video.composite_video import CompositeVideo
from vikit.common.context_managers import WorkingFolderContext
from tests.tests_tools import test_prompt_library
from vikit.music_building_context import MusicBuildingContext


class TestAudioCompositions:

    def setUp(self) -> None:
        self.sample_video_path = get_cat_video_path()
        self.prompt_loosing_faith = None
        logger.add("log_test_audio_compositions.txt", rotation="10 MB")
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_insert_subtitle_audio_no_prompt(self):
        # This test should work as we fail open: if the prompt is not provided, we should not raise an error
        vid = CompositeVideo()
        await vid._insert_subtitles_audio_recording(
            VideoBuildSettings(include_read_aloud_prompt=True, prompt=None)
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_vcomp_w_bkg_music_and_prompt_based_subtitles(self):
        with WorkingFolderContext():
            video_start = ImportedVideo(get_generated_3s_forest_video_1_path())
            video_end = ImportedVideo(get_generated_3s_forest_video_2_path())
            test_video_mixer = CompositeVideo()
            final_video = test_video_mixer.append_video(video_start).append_video(
                video_end
            )
            final_video = await final_video.build(
                VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True
                    ),
                    include_read_aloud_prompt=True,
                    prompt=test_prompt_library["moss_stones-train_boy"],
                    test_mode=False,
                )
            )
            assert final_video.media_url is not None
            assert final_video.background_music is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_apply_generated_bg_sound_on_existing_gen_videos_composite(self):
        """
        Create a single video mix with 3 imported video and default bg music
        """
        with WorkingFolderContext():
            vid1 = ImportedVideo(get_generated_3s_forest_video_1_path())
            vid2 = ImportedVideo(get_generated_3s_forest_video_2_path())

            video_comp = CompositeVideo()
            video_comp.append_video(vid1).append_video(vid2)
            await video_comp.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=True
                    ),
                    test_mode=False,
                )
            )
