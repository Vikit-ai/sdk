import unittest
import warnings
import pytest

from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.common.context_managers import WorkingFolderContext
import tests.tests_tools as tools
from vikit.video.composite_video_builder_strategy_local import (
    CompositeVideoBuilderStrategyLocal,
)
from vikit.video.composite_video import CompositeVideo
from vikit.video.raw_text_based_video import RawTextBasedVideo


class TestBuildingStrategies(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    @pytest.mark.unit
    def test_generate_video_tree_default_strategy_single_composite(self):
        """
        Test that the video tree is correctly generated, with right order,
        using a simple video tree
        """
        with WorkingFolderContext():
            build_settings = VideoBuildSettings(test_mode=True)
            composite = CompositeVideo()
            rtbv = RawTextBasedVideo("test")
            composite.append_video(rtbv)

            # Here we are testing the ordered list of video to be build
            # conforms to the expected order
            strategy = CompositeVideoBuilderStrategyLocal(
                composite_video=composite, build_order="first_videos_first"
            )
            video_build_order = strategy.prepare(
                build_settings=build_settings,
                strategy=strategy.get_first_videos_first_build_order,
            )

            assert video_build_order is not None
            # here we check the leaf has been generated first, then the root composite
            assert len(video_build_order) == 2

            assert video_build_order[0].id == rtbv.id
            assert video_build_order[1].id == composite.id
            assert isinstance(video_build_order[0], RawTextBasedVideo)
            assert isinstance(video_build_order[1], CompositeVideo)

    @pytest.mark.unit
    def test_generate_video_tree_default_strategy_mixed_composites(self):
        """
        Test that the video tree is correctly generated, with right order,
        using a  video tree including root and child composite videos
        """
        with WorkingFolderContext():
            build_settings = video_build_settings.VideoBuildSettings(test_mode=True)
            composite = CompositeVideo()
            rtbv = RawTextBasedVideo("test")
            composite.append_video(rtbv)

            # Here we are testing the ordered list of video to be build
            # conforms to the expected order
            video_build_order = CompositeVideoBuilderStrategyLocal(
                composite_video=composite, build_order="first_videos_first"
            ).prepare(build_settings=build_settings)

            assert video_build_order is not None
            # here we check the leaf has been generated first, then the root composite
            assert len(video_build_order) == 1
            assert video_build_order[0].id == rtbv.id

    @pytest.mark.local_integration
    def test_generate_video_tree_default_strategy_from_prompt_based_video(self):
        """
        Test that the video tree is correctly generated, with right order, using
        a 4 subtitles prompt based video
        """
        with WorkingFolderContext():
            build_settings = video_build_settings.VideoBuildSettings(
                run_async=False, test_mode=True
            )
            test_prompt = tools.test_prompt_library["train_boy"]
            prompt_vid = PromptBasedVideo(test_prompt)

            # Here we are testing the ordered list of video to be build
            # conforms to the expected order
            video_build_order = CompositeVideoBuilderStrategyLocal(
                video=prompt_vid.inner_composite, build_order="first_videos_first"
            ).prepare(build_settings=build_settings)

            assert video_build_order is not None
            # In this test, we have 4 subtitles, so with a promptbasedvideo we should have
            # 8 rawtextbasedvideo , 4 transitions,  4 child composite videos
            # and one final root composite videovideos

            # So first we should find the first composite made of the first subtitle used
            # to generate the first rawtextbasedvideo by reworking prompt trough keywords,
            # then a transition, then the second composite video made of the same subtitle
            # but generated from enhanced prompt.
            # then we should generate the second composite made of the second subtitle, then
            # 3rd composite made of the third subtitle, then 4th composite made of the 4th subtitle
            assert (
                video_build_order[0].id == prompt_vid.inner_composite.video_list[0].id
            ), "First video should be the first subtitle"
            assert isinstance(
                video_build_order[0], CompositeVideo
            ), f"First video should be a composite, instead we had {type(video_build_order[0])}"

            assert (
                video_build_order[1].id == prompt_vid.inner_composite.video_list[1].id
            ), "Second video should be the first transition"

    def test_async_call_to_generate_video(self):
        """
        Test that the video is generated asynchronously
        """
        with WorkingFolderContext():
            build_settings = video_build_settings.VideoBuildSettings(
                run_async=False, test_mode=True
            )
            test_prompt = tools.test_prompt_library["train_boy"]
            prompt_vid = prompt_based_video.PromptBasedVideo(test_prompt)

            built_vid = prompt_vid.build(build_settings=build_settings)

            assert built_vid is not None
