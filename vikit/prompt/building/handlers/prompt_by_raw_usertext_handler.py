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

from loguru import logger

from vikit.common.handler import Handler
from vikit.prompt.prompt_build_settings import PromptBuildSettings


class PromptByRawUserTextHandler(Handler):

    async def execute_async(
        self,
        text_prompt: str,
        **kwargs,
    ):
        """
        Process the text prompt to generate a better one more suited to generate a video,  and a title
        summarizing the prompt.

        Args:
            prompt (str): The prompt to generate the keywords from
            build_settings (PromptBuildSettings): The build settings

        Returns:
            a string containing a list of keywords to be used for video generation
        """
        logger.info(f"about to enhance a prompt from raw user text: {text_prompt}")

        prompt_build_settings: PromptBuildSettings = kwargs.get("prompt_build_settings")
        if not prompt_build_settings:
            raise ValueError("PromptBuildSettings is required to process prompt")

        logger.info(f"Processing prompt: {text_prompt}")
        (
            enhanced_prompt,
            title,
        ) = await prompt_build_settings.get_ml_models_gateway().get_enhanced_prompt_async(
            text_prompt
        )
        logger.info(
            f"Finished processing prompt, Enhanced prompt: {enhanced_prompt}, title: {title}"
        )
        return enhanced_prompt, title
