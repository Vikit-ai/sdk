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
from vikit.wrappers.ffmpeg_wrapper import merge_audio


class ReadAloudPromptAudioMergingHandler(Handler):
    """
    Handler used to apply a synthetic voice to the video, as an audio prompt
    """

    def __init__(self, recorded_prompt):
        if not recorded_prompt:
            raise ValueError("Recorded prompt is required")
        self.recorded_prompt = recorded_prompt

    async def execute_async(self, video, ml_models_gateway):
        """
        Merge prompt generated recording with video  as a single media file

        Args:
            video (Video): The video to process

        Returns:
            The video including generated synthetic voice that reads the prompt
        """
        logger.info(
            f"about to merge read aloud prompt audio to video: {video.id}, read aloud media:  {self.recorded_prompt.audio_recording}"
        )
        video.metadata.is_prompt_read_aloud = True

        video.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=self.recorded_prompt.audio_recording,
            target_file_name=video.get_file_name_by_state(
                build_settings=video.build_settings
            ),
        )
        assert video.media_url, "Media URL was not generated properly"

        return video
