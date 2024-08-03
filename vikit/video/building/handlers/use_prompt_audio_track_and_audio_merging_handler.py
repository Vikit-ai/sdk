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
from vikit.prompt.recorded_prompt import RecordedPrompt
from vikit.wrappers.ffmpeg_wrapper import merge_audio


class UsePromptAudioTrackAndAudioMergingHandler(Handler):

    async def execute_async(self, video: "Video"):
        """
        Merge music and video  as a single media file

        Args:
            video (Video): The video to process

        Returns:
            The video including generated music
        """
        logger.info(
            f"about to use recording audio track for video: {video.id}, video url : {video.media_url}"
        )
        audio_file_path = video.build_settings.prompt.audio_recording
        if audio_file_path is None:
            raise ValueError("Audio file path is required for the prompt")

        video.metadata.is_bg_music_applied = True
        video.metadata.is_subtitle_audio_applied = True
        video.background_music = audio_file_path

        video.media_url = await merge_audio(
            media_url=video.media_url,
            audio_file_path=audio_file_path,
            target_file_name=video.get_file_name_by_state(),
        )

        return video
