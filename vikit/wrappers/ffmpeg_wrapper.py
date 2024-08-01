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

import subprocess
import os
import json
import asyncio

from loguru import logger

import vikit.common.config as config
from vikit.common.decorators import log_function_params
from vikit.common.file_tools import get_canonical_name


@log_function_params
def has_audio_track(video_path):
    """
    Check if the video has an audio track

    Args:
        video_path (str): The path to the video file

    Returns:
        bool: True if the video has an audio track, False otherwise

    """

    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_streams",
        video_path,
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.debug(f"Subprocess run stdout for has_audio_track :  {result.stdout}")
    logger.debug(f"Subprocess run stderr for has_audio_track :  {result.stderr}")

    result.check_returncode()

    streams = json.loads(result.stdout)["streams"]
    return any(stream["codec_type"] == "audio" for stream in streams)


def get_media_duration(input_video_path):
    """
    Get the duration of a media file.

    Args:
        input_video_path (str): The path to the input video file.

    Returns:
        float: The duration of the media file in seconds.
    """
    assert os.path.exists(input_video_path), f"File {input_video_path} does not exist"
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            input_video_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    result.check_returncode()
    return float(float(result.stdout))

def get_media_fps(input_video_path):
    """
    Get the frames per second of a media file.

    Args:
        input_video_path (str): The path to the input video file.

    Returns:
        float: The FPS of the media file in frames per seconds.
    """
    assert os.path.exists(input_video_path), f"File {input_video_path} does not exist"

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "0",
            "-of",
            "csv=p=0",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=r_frame_rate",
            input_video_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    result.check_returncode()

    return float(str(result.stdout).split("/")[0].replace("b'", "")) / float(str(result.stdout).split("/")[1].replace("\\n'", ""))


@log_function_params
async def extract_audio_slice(
    audiofile_path: str, start: float = 0, end: float = 1, target_file_name: str = None
):
    """
    Extract a slice of the audio file using ffmpeg

    Args:
        start (int): The start of the slice
        end (int): The end of the slice
        audiofile_path (str): The path to the audio file
        target_file_name : the target file name

    Returns:
        str: The path to the extracted audio slice
    """

    logger.debug(
        f"Extracting audio slice from file  {audiofile_path} from {start} to {end}"
    )

    if not target_file_name:
        target_file_name = (
            "_".join(
                [
                    config.get_sub_audio_for_subtitle_prefix(),
                    str(float(start)),
                    "to",
                    str(float(end)),
                ]
            )
            + ".mp3"
        )
    else:
        target_file_name = target_file_name

    media_length = get_media_duration(audiofile_path)
    if end is None:
        end = media_length

    if media_length < end:
        raise ValueError("The expected audio length is longer than audio file provided")

    # Create sub part of subtitles
    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-y",
        "-ss",
        str(start),
        "-t",
        str(end),
        "-i",
        audiofile_path,
        "-acodec",
        "copy",
        target_file_name,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        error_messages = []
        if stdout:
            error_messages.append(f"stdout: {stdout.decode()}")
        if stderr:
            error_messages.append(f"stderr: {stderr.decode()}")

        if error_messages:
            error_message = "ffmpeg command failed with: " + " and ".join(
                error_messages
            )
        else:
            error_message = "ffmpeg command failed without error output"

        logger.error(error_message)
        raise Exception(error_message)

    return target_file_name


@log_function_params
async def convert_as_mp3_file(fileName, target_file_name: str):
    """
    Save the incoming audio file to a regular mp3 file with a standardised filename

    Args:

        fileName (str): The path to the audio file to convert

    Returns:
        str: The path to the converted audio file
    """
    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-y",
        "-i",
        fileName,
        target_file_name,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        error_messages = []
        if stdout:
            error_messages.append(f"stdout: {stdout.decode()}")
        if stderr:
            error_messages.append(f"stderr: {stderr.decode()}")

        if error_messages:
            error_message = "ffmpeg command failed with: " + " and ".join(
                error_messages
            )
        else:
            error_message = "ffmpeg command failed without error output"

        logger.error(error_message)
        raise Exception(error_message)

    return target_file_name


async def concatenate_videos(
    input_file: str, target_file_name=None, ratioToMultiplyAnimations=1, bias=0.33, fps=16, max_fps=16
):
    """
    Concatenate all the videos in the list using a concatenation file

    Args:
        input_file (str): The path to the input file
        target_file_name (str): The target file name
        ratioToMultiplyAnimations (int): The ratio to multiply animations
        bias (int): The bias to add to the ratio for the sound to be in sync with video frames

    Returns:
        str: The path to the concatenated video file
    """
    target_file_name = (
        target_file_name if target_file_name is not None else "TargetCompositeVideo.mp4"
    )

    if ratioToMultiplyAnimations <= 0:
        raise ValueError(
            f"Ratio to multiply animations should be greater than 0. Got {ratioToMultiplyAnimations}"
        )

    # Build the ffmpeg command
    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        input_file,
        "-vf",
        f"setpts={1 / ratioToMultiplyAnimations} * N/{fps}/TB,fps={fps * ratioToMultiplyAnimations}", #
        "-c:v",
        "libx264",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        target_file_name,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_messages = []
        if stdout:
            error_messages.append(f"stdout: {stdout.decode()}")
        if stderr:
            error_messages.append(f"stderr: {stderr.decode()}")

        if error_messages:
            error_message = "ffmpeg command failed with: " + " and ".join(
                error_messages
            )
        else:
            error_message = "ffmpeg command failed without error output"

        logger.error(error_message)
        raise Exception(error_message)

    return target_file_name  #


async def merge_audio(
    media_url: str,
    audio_file_path: str,
    audio_file_relative_volume: float = None,
    target_file_name=None,
):
    """
    Merge audio with the video

    Args:
        media_url (str): The media url to merge
        audio_file_path (str): The audio file path to merge
        audio_file_relative_volume (float): The relative volume of the audio file
        target_file_name (str): The target file name

    Returns:
        str: The merged audio file path

    """
    if not target_file_name:
        target_file_name = "merged_audio_video.mp4"

    if has_audio_track(media_url):
        merged_file = await _merge_audio_and_video_with_existing_audio(
            media_url=media_url,
            audio_file_path=audio_file_path,
            target_file_name=target_file_name,
            audio_file_relative_volume=(
                audio_file_relative_volume if audio_file_relative_volume else 1.0
            ),
        )
    else:
        merged_file = await _merge_audio_and_video_without_audio_track(
            media_url, audio_file_path, target_file_name=target_file_name
        )

    return merged_file


async def _merge_audio_and_video_with_existing_audio(
    media_url: str,
    audio_file_path: str,
    audio_file_relative_volume=1,
    target_file_name=None,
):
    """
    Merge audio with the video in the case where video already has at least oneaudio track, typically
    when the video is imported / already existing

    Args:
        media_url (str): The media url to merge
        audio_file_path (str): The audio file path to merge
        audio_file_relative_volume (float): The relative volume of the audio file
        target_file_name (str): The target file name

    Returns:
        str: The merged audio file

    """

    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-y",
        "-i",
        audio_file_path,
        "-i",
        media_url,
        "-filter_complex",
        f"[0:a]apad,loudnorm,volume={audio_file_relative_volume}[A];[1:a][A]amerge[out]",
        "-map",
        "1:v",
        "-c:v",
        "libx264",
        "-profile:v",
        "baseline",
        "-level",
        "3.0",  # This tells FFmpeg to use the H.264 Baseline Profile with a level of 3.0.
        "-pix_fmt",
        "yuv420p",  # This tells FFmpeg to use the yuv420p pixel format.
        "-map",
        "[out]",
        "-acodec",
        "aac",
        "-ar",
        "44100",  # This tells FFmpeg to use a sample rate of 44100 Hz for the audio.
        "-ac",
        "2",  # This tells FFmpeg to use 2 audio channels.
        target_file_name,
        stdout=asyncio.subprocess.PIPE,  # Capture la sortie standard
        stderr=asyncio.subprocess.PIPE,  # Capture la sortie d'erreur
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        error_messages = []
        if stdout:
            error_messages.append(f"stdout: {stdout.decode()}")
        if stderr:
            error_messages.append(f"stderr: {stderr.decode()}")

        if error_messages:
            error_message = "ffmpeg command failed with: " + " and ".join(
                error_messages
            )
        else:
            error_message = "ffmpeg command failed without error output"

        logger.error(error_message)
        raise Exception(error_message)
    return target_file_name


async def _merge_audio_and_video_without_audio_track(
    media_url: str,
    audio_file_path: str,
    target_file_name="merged_audio_video.mp4",
    audio_file_relative_volume=1,
):
    """
    Merge audio with the video in the case where video has no audio track, typically
    when generated out of a video genration ML Model

    Args:
        media_url (str): The media url to merge
        audio_file_path (str): The audio file path to merge
        audio_file_relative_volume (float): The relative volume of the audio file
        target_file_name (str): The target file name

    Returns:
        str: The merged audio file

    """
    logger.debug(f"parameters: {media_url}, {audio_file_path}, {target_file_name}")
    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-y",
        "-i",
        audio_file_path,
        "-i",
        media_url,
        "-filter_complex",
        f"[0:a]apad,loudnorm,volume={audio_file_relative_volume}[A]",
        "-shortest",
        "-map",
        "1:v",
        "-c:v",
        "libx264",
        "-profile:v",
        "baseline",
        "-level",
        "3.0",
        "-pix_fmt",
        "yuv420p",
        "-map",
        "[A]",
        "-acodec",
        "aac",
        "-ar",
        "44100",
        "-ac",
        "2",
        target_file_name,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        error_messages = []
        if stdout:
            error_messages.append(f"stdout: {stdout.decode()}")
        if stderr:
            error_messages.append(f"stderr: {stderr.decode()}")

        if error_messages:
            error_message = "ffmpeg command failed with: " + " and ".join(
                error_messages
            )
        else:
            error_message = "ffmpeg command failed without error output"

        logger.error(error_message)
        raise Exception(error_message)

    return target_file_name


async def reencode_video(video_url, target_video_name=None):
    """
    Reencode the video, doing this for imported video that might not concatenate well
    with generated ones or among themselves

    Args:
        params (tuple): The parameters to reencode the video
        video,
        video.media_url

    Returns:
        Video: The reencoded video
    """
    if video_url is None:
        raise ValueError("The video url is not provided")
    if not target_video_name:
        target_video_name = "reencoded_" + get_canonical_name(video_url) + ".mp4"

    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-y",
        "-i",
        video_url,
        "-c:v",
        "libx264",
        "-profile:v",
        "baseline",
        "-level",
        "3.0",  # This tells FFmpeg to use the H.264 Baseline Profile with a level of 3.0.
        "-pix_fmt",
        "yuv420p",  # This tells FFmpeg to use the yuv420p pixel format.
        "-acodec",
        "aac",
        "-ar",
        "44100",  # This tells FFmpeg to use a sample rate of 44100 Hz for the audio.
        "-ac",
        "2",  # This tells FFmpeg to use 2 audio channels.
        target_video_name,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        error_messages = []
        if stdout:
            error_messages.append(f"stdout: {stdout.decode()}")
        if stderr:
            error_messages.append(f"stderr: {stderr.decode()}")

        if error_messages:
            error_message = "ffmpeg command failed with: " + " and ".join(
                error_messages
            )
        else:
            error_message = "ffmpeg command failed without error output"

        logger.error(error_message)
        raise Exception(error_message)

    return target_video_name


async def get_first_frame_as_image_ffmpeg(media_url, target_path=None):
    """
    Get the first frame of the video
    """
    assert media_url, "no media URL provided"

    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-i",
        media_url,
        "-vf",
        "select=eq(n\\,0)",  # c'est un filtre vidéo qui sélectionne les frames à extraire. eq(n\,0)
        # signifie qu'il sélectionne la frame où n (le numéro de la frame) est égal à 0, c'est-à-dire la première frame
        "-vframes",  # spécifie le nombre de frames vidéo à sortir
        "1",  # on veut une seule frame
        target_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        error_messages = []
        if stdout:
            error_messages.append(f"stdout: {stdout.decode()}")
        if stderr:
            error_messages.append(f"stderr: {stderr.decode()}")

        if error_messages:
            error_message = "ffmpeg command failed with: " + " and ".join(
                error_messages
            )
        else:
            error_message = "ffmpeg command failed without error output"

        logger.error(error_message)
        raise Exception(error_message)

    return target_path


async def get_last_frame_as_image_ffmpeg(media_url, target_path=None):
    """
    Get the last frame of the video
    """
    assert media_url, "no media URL provided"

    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-sseof",  # spécifie qu'il doit commencer à x secondes de la fin du fichier.
        "-3",  # on veut les 3 dernières secondes
        "-i",
        media_url,
        "-update",  # signifie qu'il doit mettre à jour l'image de sortie si x nouvelle frame est disponible.
        "1",  # on veut une seule frame
        "-q:v",  # -q:v 1 spécifie la qualité de l'image de sortie (1 étant la meilleure qualité).
        "1",
        target_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        error_messages = []
        if stdout:
            error_messages.append(f"stdout: {stdout.decode()}")
        if stderr:
            error_messages.append(f"stderr: {stderr.decode()}")

        if error_messages:
            error_message = "ffmpeg command failed with: " + " and ".join(
                error_messages
            )
        else:
            error_message = "ffmpeg command failed without error output"

        logger.error(error_message)
        raise Exception(error_message)

    return target_path
