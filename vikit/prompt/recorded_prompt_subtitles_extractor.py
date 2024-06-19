import os
import subprocess

from loguru import logger
import pysrt

from vikit.common.decorators import log_function_params
from vikit.wrappers.ffmpeg_wrapper import extract_audio_slice, get_media_duration
import vikit.common.config as config
from vikit.prompt.subtitle_extractor import SubtitleExtractor
from vikit.gateways.ML_models_gateway import MLModelsGateway


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

    @log_function_params
    def extract_subtitles(
        self, recorded_prompt_file_path, ml_models_gateway: MLModelsGateway = None
    ):
        """
        Generate subtitles from a recorded audio file

                inputs: NA
                returns:
                    - Subtitle Rip File object
        """
        # Obtain the duration of the audio file in seconds
        if recorded_prompt_file_path is None:
            raise ValueError("The path to the recorded audio file is not provided")

        mp3_duration = get_media_duration(recorded_prompt_file_path)
        cat_command_args = ""
        video_length_per_subtitle = config.get_video_length_per_subtitle()
        for i in range(0, int(mp3_duration), video_length_per_subtitle):
            # Determine the end time for the current slice
            end = (
                mp3_duration
                if i + video_length_per_subtitle > mp3_duration
                else i + video_length_per_subtitle
            )
            # Generate the audio slice from the audio file
            generated_slice = extract_audio_slice(
                start=i, end=end, audiofile_path=recorded_prompt_file_path
            )
            logger.debug(f"Generated slice {generated_slice}")
            # Obtain  sub part of subtitles using elevenlabs API
            subs = ml_models_gateway.get_subtitles(audiofile_path=generated_slice)
            subtitle_file_path = "_".join(["subSubtitle", str(i), str(end)]) + ".srt"
            # Write subtitles to a temporary SRT file
            with open(subtitle_file_path, "a") as f:
                f.write(subs["transcription"])

            # Append SRT file path to cat command arguments
            cat_command_args = " ".join([cat_command_args, subtitle_file_path])

            # Concatenate the temporary SRT files to a prompt wide srt file
            with open(config.get_subtitles_default_file_name(), "w") as f:
                p = subprocess.Popen(
                    ["cat"] + cat_command_args.split(), stdout=f, stderr=subprocess.PIPE
                )
                stdout, stderr = p.communicate()
                if p.returncode != 0:
                    raise subprocess.CalledProcessError(
                        p.returncode, p.args, output=stdout, stderr=stderr
                    )

            assert os.path.exists(
                config.get_subtitles_default_file_name()
            ), "The generated subtitles file does not exists after having generating subtitles from audio file"
            subs = pysrt.open(config.get_subtitles_default_file_name())

        return subs
