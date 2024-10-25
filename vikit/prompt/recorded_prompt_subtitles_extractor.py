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
import subprocess

import pysrt
from loguru import logger

import vikit.common.config as config
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.prompt.subtitle_extractor import SubtitleExtractor
from vikit.wrappers.ffmpeg_wrapper import extract_audio_slice, get_media_duration
import uuid


class RecordedPromptSubtitlesExtractor(SubtitleExtractor):
    """
    A class to extract subtitles from a sound recording,
    merge short subtitles into longer ones, or extract them as text tokens

    Here is how we do it:
    - We extract the audio slice from the audio file and cap the duration of the slice to x seconds
    so that replicate can process it (today n = 300 seconds, i.e. 5minutes)
    - We save the generated subtitles to a temporary SRT file
    - We concatenate the temporary SRT files to a prompt wide srt file

    Yes this is kind of hacky, but it works for now.
    """

    async def extract_subtitles_async(
        self, recorded_prompt_file_path, ml_models_gateway: MLModelsGateway = None
    ):
        """
        Generate subtitles from a recorded audio file

                inputs: NA
                returns: Subtitle Rip File object
        """
        # Obtain the duration of the audio file in seconds
        if recorded_prompt_file_path is None:
            raise ValueError("The path to the recorded audio file is not provided")

        subs = None
        mp3_duration = get_media_duration(recorded_prompt_file_path)
        cat_command_args = ""
        video_length_per_subtitle = config.get_video_length_per_subtitle()
        secondsToAdd = 0
        for i in range(0, int(mp3_duration), video_length_per_subtitle):
            # Determine the end time for the current slice
            end = (
                mp3_duration
                if i + video_length_per_subtitle > mp3_duration
                else i + video_length_per_subtitle
            )
            # Generate the audio slice from the audio file
            generated_slice = await extract_audio_slice(
                start=i, end=end, audiofile_path=recorded_prompt_file_path
            )
            logger.debug(f"Generated slice {generated_slice}")
            # Obtain  sub part of subtitles using elevenlabs API
            subs = await ml_models_gateway.get_subtitles_async(
                audiofile_path=generated_slice
            )
            logger.debug(f"Subtitles in subtitle extractor: {subs}")

            subtitle_file_path = "_".join(["subSubtitle", str(i), str(end)]) + ".srt"

            if "output" in subs:
                if "transcription" in subs["output"]:
                    transcription = subs["output"]["transcription"]
                else:
                    raise ValueError(
                        "Error: 'transcription' key exists but has no content."
                    )
            else:
                if "transcription" in subs:
                    transcription = subs["transcription"]
                else:
                    raise ValueError(
                        "Error: 'transcription' key exists but has no content."
                    )
            with open(subtitle_file_path, "w") as f:
                f.write(transcription)

            # We shift subtitles if this is not the first file
            currentSubtitles = pysrt.open(subtitle_file_path)
            currentSubtitles.shift(seconds=secondsToAdd)
            currentSubtitles.save(subtitle_file_path)

            # We save the new time of the last subtitle to add it to the next batch of subtitles
            last_subtitle = currentSubtitles[-1]
            secondsToAdd = (
                last_subtitle.end.hours * 3600
                + last_subtitle.end.minutes * 60
                + last_subtitle.end.seconds
            )

            # Append SRT file path to cat command arguments
            cat_command_args = " ".join([cat_command_args, subtitle_file_path])

            # Concatenate the temporary SRT files to a prompt wide srt file
            tempUuid = self.prompt_factory_uuid = str(uuid.uuid4())
            with open(config.get_subtitles_default_file_name(tempUuid), "w") as f:
                p = subprocess.Popen(
                    ["cat"] + cat_command_args.split(), stdout=f, stderr=subprocess.PIPE
                )
                stdout, stderr = p.communicate()
                if p.returncode != 0:
                    raise subprocess.CalledProcessError(
                        p.returncode, p.args, output=stdout, stderr=stderr
                    )

            assert os.path.exists(
                config.get_subtitles_default_file_name(tempUuid)
            ), "The generated subtitles file does not exists after having generating subtitles from audio file"
            subs = pysrt.open(config.get_subtitles_default_file_name(tempUuid))

        return subs
