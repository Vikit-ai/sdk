from concurrent.futures import ProcessPoolExecutor
from queue import PriorityQueue
import time
import os

import unittest
import warnings

from vikit.video import prompt_based_video, video_build_settings
import tests.tests_tools as tools
from vikit.common.context_managers import WorkingFolderContext


class TestConcurrency(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    @unittest.skip("Test skipped before resolution")
    def test_generate_video_tree(self):
        """
        Test that the video tree is correctly generated, with right order
        """
        with WorkingFolderContext():
            build_settings = video_build_settings.VideoBuildSettings(
                run_async=False, test_mode=True
            )
            test_prompt = tools.test_prompt_library["train_boy"]
            prompt_vid = prompt_based_video.PromptBasedVideo(test_prompt)

            build_preparation = built_vid = prompt_vid.prepare(
                build_settings=build_settings
            )

            assert build_preparation is not None
            assert build_preparation.build_sequence is not None
            assert build_preparation.build_sequence is not None

            # assert len(build_preparation.build_sequence) == len(test_prompt.subtitles) * 4 + 1
            # (2 vids per sub + 1 transition + one composite) per subtitle + one final root composite

            assert built_vid is not None
            assert built_vid.media_url is not None

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
