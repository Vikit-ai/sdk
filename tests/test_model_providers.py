import warnings
import pytest
from loguru import logger

from vikit.video.video import VideoBuildSettings
from vikit.video.composite_video import CompositeVideo
from vikit.common.context_managers import WorkingFolderContext
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.music_building_context import MusicBuildingContext
from tests.testing_tools import test_prompt_library
import tests.testing_tools as tools  # used to get a library of test prompts

prompt_mystic = tools.test_prompt_library["moss_stones-train_boy"]
logger.add("log_test_model_providers.txt", rotation="10 MB")
warnings.simplefilter("ignore", category=ResourceWarning)
warnings.simplefilter("ignore", category=UserWarning)


class TestModelProviders:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_mix_providers_and_generate(self):
        with WorkingFolderContext():
            final_composite_video = CompositeVideo()
            # train_boy has 4 subtitles
            for i, subtitle in enumerate(test_prompt_library["train_boy"].subtitles):
                if i % 3 == 0:
                    target_model_provider = "vikit"
                elif i % 3 == 1:
                    target_model_provider = ""
                elif i % 3 == 2:
                    target_model_provider = "videocrafter"
                else:
                    target_model_provider = (None,)

                video = RawTextBasedVideo(subtitle.text)
                await video.prepare_build_hook(
                    build_settings=VideoBuildSettings(
                        test_mode=False,
                        music_building_context=MusicBuildingContext(),
                        target_model_provider=target_model_provider,
                    )
                )
                final_composite_video.append_video(video)

            await final_composite_video.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=True
                    ),
                    test_mode=False,
                    include_read_aloud_prompt=True,
                    prompt=test_prompt_library["train_boy"],
                )
            )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_haiper_provider_and_generate(self):
        with WorkingFolderContext():
            await self._chose_provider_and_generate(provider="haiper")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_choose_provider_and_generate(self):
        with WorkingFolderContext():
            await self._chose_provider_and_generate(provider="vikit")
            await self._chose_provider_and_generate(provider="stabilityai")
            await self._chose_provider_and_generate(provider="haiper")
            await self._chose_provider_and_generate(provider="videocrafter")

    async def _chose_provider_and_generate(self, provider="videocrafter"):
        with WorkingFolderContext():
            final_composite_video = CompositeVideo()
            # train_boy has 4 subtitles
            video = RawTextBasedVideo("This is a fantastic day today")
            await video.prepare_build_hook(
                build_settings=VideoBuildSettings(
                    test_mode=False,
                    music_building_context=MusicBuildingContext(),
                    target_model_provider=provider,
                )
            )
            final_composite_video.append_video(video)

            await final_composite_video.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=True
                    ),
                    test_mode=False,
                )
            )
