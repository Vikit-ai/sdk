# Copyright 2024 Vikit.ai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import os

import pysrt
from loguru import logger

from vikit.prompt.prompt import Prompt
from vikit.prompt.prompt_build_settings import PromptBuildSettings
from vikit.prompt.prompt_factory import PromptFactory
from vikit.video.composite_video import CompositeVideo
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.seine_transition import SeineTransition
from vikit.video.video import VideoBuildSettings
from vikit.video.video_types import VideoType


class PromptBasedVideo(CompositeVideo):
    """
    PromptBasedVideo is a simple way to generate a video based out of a text prompt

    It creates a master composite video which embeds as many composite video as there are subtitles
    in the given prompt.

    We do some form of inheritance by composition to prevent circular dependencies and benefit from more modularity
    """

    def __init__(self, prompt: Prompt = None):
        if not prompt:
            raise ValueError("prompt cannot be None")
        self._prompt = prompt

        super().__init__()

    def __str__(self) -> str:
        super_str = super().__str__()
        return super_str + os.linesep + f"Prompt: {self._prompt}"

    @property
    def short_type_name(self):
        """
        Get the short type name of the video
        """
        return str(VideoType.PRMPTBASD)

    def get_title(self):
        """
        Title of the prompt based video, generated from an LLM. If not available, we generate it from the prompt
        """
        if not self.metadata.title:
            # backup plan: If no title existing yet (should be generated straight from an LLM)
            # then get the first and last words of the prompt
            splitted_prompt = self._prompt.subtitles[0].text.split(" ")
            clean_title_words = [word for word in splitted_prompt if word.isalnum()]
            if len(clean_title_words) == 1:
                summarised_title = clean_title_words[0]
            else:
                summarised_title = clean_title_words[0] + "-" + clean_title_words[-1]
            self.metadata.title = summarised_title

        return self.metadata.title

    async def prepare_build(self, build_settings=VideoBuildSettings()):
        """
        Generate the actual inner video

        Params:
            - build_settings: allow some customization

        Returns:
            The current instance
        """
        super().prepare_build(build_settings=build_settings)
        return await self.compose(build_settings=build_settings)

    async def compose(self, build_settings: VideoBuildSettings):
        """
        Compose the inner composite video

        Params:
            - build_settings: allow some customization

        Returns:
            The inner composite video
        """
        self._is_root_video_composite = True
        if not build_settings.prompt:
            logger.warning(
                "No prompt found in the build settings, using the default one"
            )
            build_settings.prompt = self._prompt

        for sub in self._prompt.subtitles:
            vid_cp_sub = CompositeVideo()
            (
                keyword_based_vid,
                prompt_based_vid,
                transit,
            ) = await self._prepare_basic_building_block(sub, build_stgs=build_settings)

            vid_cp_sub.append_video(keyword_based_vid).append_video(
                transit
            ).append_video(
                prompt_based_vid
            )  # Building a set of 2 videos around the same text + a transition

            self.append_video(vid_cp_sub)  # Adding the comnposite to the overall video

        return self

    async def _prepare_basic_building_block(
        self, sub: pysrt.SubRipItem, build_stgs: VideoBuildSettings = None
    ):
        """
        build the basic building block of the full video/
        - One RawTextBasedVideo from the keyword
        - One RawTextBasedVideo from the prompt
        - One SeineTransition between the two

        Calling prepare_build allows for injecting dedicated build settings for each video
        and not the default on from the parent composite

        Params:
            - sub_text: the subtitle text
            - build_stgs: the VideoBuildSettings

        Returns:
            - keyword_based_vid: the video generated from the keyword
            - prompt_based_vid: the video generated from the prompt
            - transit: the transition between the two
        """

        prompt_fact = PromptFactory(
            prompt_build_settings=PromptBuildSettings(test_mode=build_stgs.test_mode)
        )
        enhanced_prompt_from_keywords = (
            await prompt_fact.get_reengineered_prompt_text_from_raw_text(
                prompt=sub.text,
                prompt_build_settings=PromptBuildSettings(
                    test_mode=build_stgs.test_mode,
                    generate_from_llm_keyword=True,
                    generate_from_llm_prompt=False,
                ),
            )
        )

        keyword_based_vid = await RawTextBasedVideo(sub.text).prepare_build(
            build_settings=VideoBuildSettings(
                prompt=enhanced_prompt_from_keywords,
                test_mode=build_stgs.test_mode,
                target_model_provider=build_stgs.target_model_provider,
                interpolate=build_stgs.interpolate,
            )
        )

        enhanced_prompt_from_prompt_text = (
            await prompt_fact.get_reengineered_prompt_text_from_raw_text(
                prompt=sub.text,
                prompt_build_settings=PromptBuildSettings(
                    test_mode=build_stgs.test_mode,
                    generate_from_llm_keyword=False,
                    generate_from_llm_prompt=True,
                ),
            )
        )
        prompt_based_vid = await RawTextBasedVideo(sub.text).prepare_build(
            build_settings=VideoBuildSettings(
                prompt=enhanced_prompt_from_prompt_text,
                test_mode=build_stgs.test_mode,
                target_model_provider=build_stgs.target_model_provider,
                interpolate=build_stgs.interpolate,
            )
        )
        assert keyword_based_vid is not None, "keyword_based_vid cannot be None"
        assert prompt_based_vid is not None, "prompt_based_vid cannot be None"

        transit = SeineTransition(
            source_video=keyword_based_vid,
            target_video=prompt_based_vid,
        )

        return keyword_based_vid, prompt_based_vid, transit
