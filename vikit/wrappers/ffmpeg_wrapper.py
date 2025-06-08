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

import asyncio
import json
import os
import subprocess
import ffmpeg  # Importation de la bibliothèque ffmpeg-python

from loguru import logger

import vikit.common.config as config
from vikit.common.decorators import log_function_params
from vikit.common.file_tools import get_canonical_name


async def extract_audio_from_video(video_full_path, target_dir: str = None) -> str:
    """
    Extract all audio tracks from a video and output them as separate files.
    Naive implementation:
        - we do not check the existence of audio stream,
        - we do not check the pre-existence of the output file,

    Args:
        video_full_path (str): Full path of the input video file.
        target_dir: Directory where to store audio file

    Returns:
       The output audio file path

    """
    if not video_full_path:
        raise ValueError("No video file path provided")

    if not os.path.exists(video_full_path):
        logger.error(f"File {video_full_path} does not exist")
        raise FileNotFoundError(f"File {video_full_path} does not exist")

    # set the output file
    logger.debug(f"Extracting audio from {video_full_path} to {target_dir}")

    final_name = get_canonical_name(video_full_path) + "_extracted_audio.wav"

    if target_dir:
        if not os.path.exists(target_dir):  # Fail open
            os.makedirs(target_dir)
        target_file_path = os.path.join(
            target_dir,
            final_name,
        )
    else:
        target_file_path = final_name

    logger.debug(f"Extracting audio from {video_full_path} to {target_file_path}")

    if os.path.exists(target_file_path):  # Fail open
        logger.debug(f"File {target_file_path} already exists. Skipping extraction")
        return target_file_path

    # The command you want to execute
    # TODO: allow for encoding and frequency selection by end user
    cmd = ["ffmpeg", "-i", video_full_path, target_file_path]

    logger.debug(" ".join(cmd))

    # Execute the command
    subprocess.run(cmd, check=True)

    assert os.path.exists(target_file_path), f"File {target_file_path} does not exist"

    return target_file_path


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

    cmd = (
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
    )
    await _run_command(cmd)
    return target_file_name


async def convert_as_mp3_file(fileName, target_file_name: str):
    """
    Save the incoming audio file to a regular mp3 file with a standardized filename

    Args:

        fileName (str): The path to the audio file to convert

    Returns:
        str: The path to the converted audio file
    """

    cmd = ("ffmpeg", "-y", "-i", fileName, target_file_name)
    await _run_command(cmd)
    return target_file_name


def get_video_resolution(file_path: str) -> tuple[int, int]:
    """Récupère la résolution (largeur, hauteur) en utilisant ffmpeg.probe."""
    logger.debug(f"Sondage de {file_path} pour la résolution...")
    probe = ffmpeg.probe(file_path)
    video_stream = next(
        (s for s in probe["streams"] if s["codec_type"] == "video"), None
    )
    if not video_stream:
        raise ValueError(f"Aucun flux vidéo trouvé dans {file_path}")
    return int(video_stream["width"]), int(video_stream["height"])


def get_media_fps(file_path: str) -> float:
    """Récupère les FPS en utilisant ffmpeg.probe."""
    logger.debug(f"Sondage de {file_path} pour les FPS...")
    probe = ffmpeg.probe(file_path)
    video_stream = next(
        (s for s in probe["streams"] if s["codec_type"] == "video"), None
    )
    if not video_stream or "r_frame_rate" not in video_stream:
        raise ValueError(f"Impossible de déterminer les FPS pour {file_path}")
    num, den = map(int, video_stream["r_frame_rate"].split("/"))
    return num / den if den != 0 else 0


def has_audio_track(file_path: str) -> bool:
    """Vérifie la présence d'une piste audio en utilisant ffmpeg.probe."""
    logger.debug(f"Sondage de {file_path} pour une piste audio...")
    probe = ffmpeg.probe(file_path)
    return any(s["codec_type"] == "audio" for s in probe["streams"])


def get_media_duration(file_path: str) -> float:
    """Récupère la durée en utilisant ffmpeg.probe."""
    logger.debug(f"Sondage de {file_path} pour la durée...")
    probe = ffmpeg.probe(file_path)
    return float(probe["format"]["duration"])


def get_audio_properties(file_path: str) -> tuple[int, str]:
    """Récupère les propriétés audio en utilisant ffmpeg.probe."""
    logger.debug(f"Sondage de {file_path} pour les propriétés audio...")
    try:
        probe = ffmpeg.probe(file_path)
        audio_stream = next(
            (s for s in probe["streams"] if s["codec_type"] == "audio"), None
        )
        if not audio_stream:
            # Retourne des valeurs par défaut si aucune piste audio n'est trouvée
            return 48000, "stereo"

        sample_rate = int(audio_stream.get("sample_rate", 48000))
        channel_layout = audio_stream.get("channel_layout", "stereo")

        # 'n/a' peut être une valeur pour le channel_layout
        if channel_layout.lower() == "n/a":
            channel_layout = "stereo"

        return sample_rate, channel_layout
    except Exception as e:
        logger.warning(
            f"Erreur lors de la récupération des propriétés audio pour {file_path}: {e}. Utilisation des valeurs par défaut."
        )
        return 48000, "stereo"


async def concatenate_videos(
    video_file_paths: list[str],
    target_file_name: str = None,
    ratio_to_multiply_animations: float = 1,
    fps: int | None = None,
) -> str:
    """
    Concatène des vidéos en utilisant la bibliothèque ffmpeg-python.
    """
    if not video_file_paths:
        raise ValueError("La liste video_file_paths ne peut pas être vide.")

    target_file_name = target_file_name or "TargetCompositeVideo.mp4"

    # Détermination des propriétés cibles
    ref_width, ref_height = get_video_resolution(video_file_paths[0])
    target_fps = fps if fps else get_media_fps(video_file_paths[0])
    logger.debug(f"Propriétés cibles : {ref_width}x{ref_height} @ {target_fps:.2f} FPS")

    # Création des flux d'entrée
    inputs = [ffmpeg.input(path) for path in video_file_paths]

    # Traitement de chaque flux vidéo
    processed_videos = []
    for stream in inputs:
        processed_v = (
            stream.video.filter(
                "scale",
                w=ref_width,
                h=ref_height,
                force_original_aspect_ratio="decrease",
            )
            .filter("pad", w=ref_width, h=ref_height, x="(ow-iw)/2", y="(oh-ih)/2")
            .filter("fps", fps=target_fps)
            .filter("setpts", f"{1 / ratio_to_multiply_animations:.6f}*PTS")
        )
        processed_videos.append(processed_v)

    # Vérification et traitement des flux audio
    audio_flags = [has_audio_track(path) for path in video_file_paths]

    if not any(audio_flags):
        # Cas 1 : Aucune vidéo n'a d'audio
        logger.debug("Aucun audio. Concaténation vidéo uniquement.")
        concatenated_stream = ffmpeg.concat(*processed_videos, v=1, a=0)
    else:
        # Cas 2 : Au moins une vidéo a de l'audio
        logger.debug(
            "Audio détecté. Normalisation et génération de silence si nécessaire."
        )

        # Propriétés audio de référence
        ref_audio_path = next(
            path for i, path in enumerate(video_file_paths) if audio_flags[i]
        )
        ref_sample_rate, ref_channel_layout = get_audio_properties(ref_audio_path)
        logger.debug(
            f"Propriétés audio de référence : {ref_sample_rate}Hz, {ref_channel_layout}"
        )

        processed_audios = []
        for i, stream in enumerate(inputs):
            if audio_flags[i]:
                # Traiter le flux audio existant
                processed_a = (
                    stream.audio.filter(
                        "aformat",
                        sample_rates=ref_sample_rate,
                        channel_layouts=ref_channel_layout,
                    )
                    .filter("asetpts", "PTS-STARTPTS")
                    .filter("atempo", f"{ratio_to_multiply_animations:.6f}")
                )
                processed_audios.append(processed_a)
            else:
                # Générer un flux de silence
                duration = (
                    get_media_duration(video_file_paths[i])
                    / ratio_to_multiply_animations
                )
                silent_a = ffmpeg.input(
                    f"anullsrc",
                    f="lavfi",
                    channel_layout=ref_channel_layout,
                    sample_rate=ref_sample_rate,
                ).filter("atrim", duration=duration)
                processed_audios.append(silent_a)

        # Concaténer les flux vidéo et audio traités
        concatenated_stream = ffmpeg.concat(
            *processed_videos, *processed_audios, v=1, a=1
        )

    # Définition de la sortie et exécution de la commande
    logger.debug("Construction et exécution de la commande ffmpeg...")
    process = (
        ffmpeg.output(
            concatenated_stream,
            target_file_name,
            **{
                "c:v": "libx264",
                "crf": 23,
                "preset": "fast",
                "c:a": "aac",
                "b:a": "192k",
            },
        )
        .overwrite_output()
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )

    # Attendre la fin du processus
    stdout, stderr = await process.wait()

    if process.returncode != 0:
        logger.error(f"Erreur FFmpeg : {stderr.decode()}")
        raise RuntimeError(f"FFmpeg a échoué avec le code {process.returncode}")

    logger.info(f"Vidéo concaténée avec succès : {target_file_name}")


async def merge_audio(
    media_url: str,
    audio_file_path: str,
    audio_file_relative_volume: float | None = None,
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
    audio_file_relative_volume=1.0,
    target_file_name=None,
):
    """
    Merge audio with the video in the case where video already has at least one audio
    track, typically when the video is imported / already existing

    Args:
        media_url (str): The media url to merge
        audio_file_path (str): The audio file path to merge
        audio_file_relative_volume (float): The relative volume of the audio file
        target_file_name (str): The target file name

    Returns:
        str: The merged audio file

    """
    media_url_to_use = media_url
    # Special case
    if target_file_name == media_url:
        new_media_name = media_url.split(".")[0] + "_." + media_url.split(".")[1]
        logger.debug("Renaming file : ffmpeg mv " + media_url + " " + new_media_name)
        await asyncio.create_subprocess_exec("mv", media_url, new_media_name)
        media_url_to_use = media_url.split(".")[0] + "_." + media_url.split(".")[1]

    cmd = (
        "ffmpeg",
        "-y",
        "-i",
        audio_file_path,
        "-i",
        media_url_to_use,
        "-filter_complex",
        (
            f"[0:a]apad,loudnorm,volume={audio_file_relative_volume},"
            "aformat=sample_fmts=u8|s16:channel_layouts=stereo[A];[1:a][A]amerge[out]"
        ),
        "-map",
        "1:v",
        "-c:v",
        "libx264",
        "-profile:v",
        "baseline",
        # This tells FFmpeg to use the H.264 Baseline Profile with a level of 3.0.
        "-level",
        "3.0",
        # This tells FFmpeg to use the yuv420p pixel format.
        "-pix_fmt",
        "yuv420p",
        "-map",
        "[out]",
        "-acodec",
        "aac",
        # This tells FFmpeg to use a sample rate of 44100 Hz for the audio.
        "-ar",
        "44100",
        # This tells FFmpeg to use 2 audio channels.
        "-ac",
        "2",
        target_file_name,
    )
    await _run_command(cmd)
    return target_file_name


async def _merge_audio_and_video_without_audio_track(
    media_url: str,
    audio_file_path: str,
    target_file_name="merged_audio_video.mp4",
    audio_file_relative_volume=1,
):
    """
    Merge audio with the video in the case where video has no audio track, typically
    when generated out of a video generation ML Model

    Args:
        media_url (str): The media url to merge
        audio_file_path (str): The audio file path to merge
        audio_file_relative_volume (float): The relative volume of the audio file
        target_file_name (str): The target file name

    Returns:
        str: The merged audio file

    """
    logger.debug(f"parameters: {media_url}, {audio_file_path}, {target_file_name}")

    cmd = (
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
    )
    await _run_command(cmd)
    return target_file_name


async def reencode_video(video_url, target_video_name=None):
    """
    Reencode the video, doing this for imported video that might not concatenate well
    with generated ones or among themselves

    Args:
        video_url (str): The video url to reencode
        target_video_name (str): The target video name

    Returns:
        Video: The reencoded video
    """
    if video_url is None:
        raise ValueError("The video url is not provided")
    if not target_video_name:
        target_video_name = "reencoded_" + get_canonical_name(video_url) + ".mp4"

    logger.trace("Re-encoding video " + video_url + " with name " + target_video_name)

    cmd = (
        "ffmpeg",
        "-y",
        "-i",
        video_url,
        "-filter:v",
        "fps=24",
        "-c:v",
        "libx264",
        "-profile:v",
        "baseline",
        # This tells FFmpeg to use the H.264 Baseline Profile with a level of 3.0.
        "-level",
        "3.0",
        # This tells FFmpeg to use the yuv420p pixel format.
        "-pix_fmt",
        "yuv420p",
        "-acodec",
        "aac",
        # This tells FFmpeg to use a sample rate of 44100 Hz for the audio.
        "-ar",
        "44100",
        # This tells FFmpeg to use 2 audio channels.
        "-ac",
        "2",
        target_video_name,
    )
    await _run_command(cmd)
    return target_video_name


# TODO: remove unused parameter target_duration
async def cut_video(
    video_url, start_time, end_time, target_duration=None, target_video_name=None
):
    """
    Cuts the video starting at start_time and ending at end_time
    Args:
        video_url (str): The video url to cut (eg ./videofolder/video.mp4)
        start_time (float): The begining time of the video in seconds
        end_time (float): The end time of the video in seconds
        target_duration (float) : Optional, the duration of the output video in seconds
        target_video_name (string) : Optional, the name of the output video in seconds

    Returns:
        Video: The reencoded video
    """

    assert video_url, "no media URL provided"

    if not target_video_name:
        target_video_name = "cutted_" + get_canonical_name(video_url) + ".mp4"

    cmd = (
        "ffmpeg",
        "-y",
        "-i",
        video_url,
        "-ss",
        str(start_time),
        "-to",
        str(end_time),
        "-c:v",
        "libx264",
        target_video_name,
    )
    await _run_command(cmd)
    return target_video_name


async def get_first_frame_as_image_ffmpeg(media_url, target_path=None):
    """
    Get the first frame of the video
    """
    assert media_url, "no media URL provided"

    cmd = (
        "ffmpeg",
        "-y",
        "-i",
        media_url,
        # It is a video filter that selects the frames to extract eq(n\\,0) means it
        # selects the frame where n (the frame number) is equal to 0, in other word,
        # the first frame.
        "-vf",
        "select=eq(n\\,0)",
        # Output a single frame.
        "-vframes",
        "1",
        target_path,
    )
    await _run_command(cmd)
    return target_path


async def reverse_video(
    video_url,
    target_video_name=None,
):
    """
    Reverses the frames of the video, with last frame being the first, second to last
    the second etc... and first frame the latest one
    Args:
        video_url (str): The video to reverse
        target_video_name (string) : Optional, the name of the output video

    Returns:
        Video: The reversed video
    """
    assert video_url, "no media URL provided"

    if not target_video_name:
        target_video_name = "reversed_" + get_canonical_name(video_url) + ".mp4"
    # ffmpeg -i example.mp4 -vf reverse -an output_r.mp4
    cmd = ("ffmpeg", "-i", video_url, "-vf", "reverse", target_video_name)
    await _run_command(cmd)
    return target_video_name


async def create_zoom_video(
    image_url,
    target_duration=3,
    target_video_name=None,
):
    """
    Creates a video zooming into an image for a certain duration
    Args:
        image_url (str): The image url to zoom in
        target_duration (float) : Optional, the duration of the output video in seconds
        target_video_name (string) : Optional, the name of the output video

    Returns:
        Video: The zoomed video
    """

    assert image_url, "no media URL provided"

    if not target_video_name:
        target_video_name = "zoom_" + get_canonical_name(image_url) + ".mp4"

    cmd = (
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        image_url,
        "-vf",
        (
            "scale=16000:-1,"
            "zoompan="
            "z='min(zoom+0.008,2)':"
            "x='iw/2-(iw/zoom/2)':"
            "y='ih/2-(ih/zoom/2)':"
            "d=125,"
            "fps=24"
        ),
        "-c:v",
        "libx264",
        "-t",
        str(target_duration),
        target_video_name,
    )
    await _run_command(cmd)
    return target_video_name


async def get_last_frame_as_image_ffmpeg(media_url, target_path=None):
    """
    Get the last frame of the video
    """
    assert media_url, "no media URL provided"

    cmd = (
        "ffmpeg",
        # Include the last 3 seconds of the video
        "-sseof",
        "-3",
        "-i",
        media_url,
        # Update the output image if a new frame is available to a single frame.
        "-update",
        "1",
        # Specifies the quality of the output image (1 being the best quality).
        "-q:v",
        "1",
        target_path,
    )
    await _run_command(cmd)
    return target_path


async def generate_video_from_image(
    image_url, duration=5, dimensions=(1280, 720), target_path=None
):
    """
    Generates a video from an image
    """
    assert image_url, "no media URL provided"

    if not target_path:
        target_path = "animated_" + get_canonical_name(image_url) + ".mp4"

    cmd = (
        "ffmpeg",
        "-y",
        # Loops on first frame, the image
        "-loop",
        "1",
        # Specifies first frame as the image
        "-i",
        image_url,
        # The encoding library
        "-c:v",
        "libx264",
        # Specifying the duration
        "-t",
        str(duration),
        # Specifying dimensions, should be a multiple of 2
        "-vf",
        "scale=" + str(dimensions[0]) + ":" + str(dimensions[1]),
        target_path,
    )
    await _run_command(cmd)
    return target_path


async def _run_command(cmd: tuple[str]):
    logger.debug(" ".join(cmd))

    process = await asyncio.create_subprocess_exec(
        *cmd,
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
