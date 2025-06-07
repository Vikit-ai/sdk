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

    logger.debug(" ".join(command))

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.trace(f"Subprocess run stdout for has_audio_track :  {result.stdout}")
    logger.trace(f"Subprocess run stderr for has_audio_track :  {result.stderr}")

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

    cmd = (
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        input_video_path,
    )

    logger.debug(" ".join(cmd))

    result = subprocess.run(
        [
            *cmd,
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

    cmd = (
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
    )

    logger.debug(" ".join(cmd))

    result = subprocess.run(
        [
            *cmd,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    result.check_returncode()

    # Extract the denominator of the frame rate fraction
    result_stdout = str(result.stdout).split("/")[1].strip().replace("\\n'", "")

    # Handle cases where the extracted value ends with an unwanted character
    if result_stdout.endswith((".", ",")):
        result_stdout = result_stdout[:-1] + (
            "0" if result_stdout.endswith(".") else "."
        )

    # Compute FPS by dividing the numerator by the denominator

    return float(str(result.stdout).split("/")[0].replace("b'", "")) / float(
        result_stdout
    )


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


def get_video_resolution(video_path):
    """Récupère la résolution (width, height) d'une vidéo via ffprobe"""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "json",
        video_path,
    ]
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
    )
    info = json.loads(result.stdout)
    width = info["streams"][0]["width"]
    height = info["streams"][0]["height"]
    return width, height


# Configuration du logger (vous pouvez l'adapter à votre projet)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# --- Fonctions d'assistance (à compléter avec vos implémentations existantes) ---


async def _run_command(cmd: list[str]):
    """Exécute une commande shell."""
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logger.error(f"Erreur FFmpeg: {stderr.decode()}")
        raise RuntimeError(f"FFmpeg a échoué avec le code {process.returncode}")
    logger.debug(f"FFmpeg a terminé avec succès: {stdout.decode()}")


def get_video_resolution(file_path: str) -> tuple[int, int]:
    """Récupère la résolution (largeur, hauteur) d'une vidéo."""
    # Votre implémentation ici...
    # Exemple :
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=s=x:p=0",
        file_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    width, height = map(int, result.stdout.strip().split("x"))
    return width, height


def get_media_fps(file_path: str) -> float:
    """Récupère le FPS d'une vidéo."""
    # Votre implémentation ici...
    # Exemple :
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=r_frame_rate",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    num, den = map(int, result.stdout.strip().split("/"))
    return num / den if den else 0


def has_audio_track(file_path: str) -> bool:
    """Vérifie si une vidéo a une piste audio."""
    # Votre implémentation ici...
    # Exemple :
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a",
        "-show_entries",
        "stream=codec_type",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() != ""


def get_media_duration(file_path: str) -> float:
    """Récupère la durée d'un média en secondes."""
    # Votre implémentation ici...
    # Exemple :
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


# --- NOUVELLE fonction d'assistance pour les propriétés audio ---


def get_audio_properties(file_path: str) -> tuple[int, str]:
    """
    Récupère la fréquence d'échantillonnage et la disposition des canaux du premier flux audio.
    Retourne (fréquence, disposition), par ex. (48000, 'stereo').
    Utilise des valeurs par défaut sûres en cas d'échec.
    """
    try:
        command = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=sample_rate,channel_layout",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file_path,
        ]
        logger.debug(f"Exécution de ffprobe: {' '.join(command)}")
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding="utf-8"
        )
        output = result.stdout.strip().split("\n")
        if len(output) >= 2:
            sample_rate = int(output[0])
            channel_layout = output[1]
            return sample_rate, channel_layout
        else:
            logger.warning(
                f"Impossible de parser les propriétés audio de {file_path}. Utilisation des valeurs par défaut."
            )
            return 48000, "stereo"
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        ValueError,
        IndexError,
    ) as e:
        logger.warning(
            f"Erreur lors de la récupération des propriétés audio pour {file_path}: {e}. Utilisation des valeurs par défaut."
        )
        return 48000, "stereo"


# --- Fonction principale refactorisée ---


async def concatenate_videos(
    video_file_paths: list[str],
    target_file_name: str = None,
    ratio_to_multiply_animations: float = 1,
    fps: int | None = None,
) -> str:
    """
    Concatène plusieurs fichiers vidéo en un seul, en gérant correctement les
    pistes audio manquantes en générant du silence.
    """
    if not video_file_paths:
        raise ValueError("La liste video_file_paths doit contenir au moins un élément")

    if ratio_to_multiply_animations <= 0:
        raise ValueError("ratio_to_multiply_animations doit être > 0")

    target_file_name = target_file_name or "TargetCompositeVideo.mp4"

    width, height = get_video_resolution(video_file_paths[0])
    logger.debug(f"Utilisation de la résolution de référence: {width}x{height}")

    cmd = ["ffmpeg", "-y"]
    video_filter_parts = []
    fps_values = []
    audio_flags = []

    for idx, path in enumerate(video_file_paths):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Fichier non trouvé: {path}")

        cmd.extend(["-i", path])

        video_fps = get_media_fps(path)
        if video_fps <= 0:
            raise ValueError(f"FPS invalide ({video_fps}) dans le fichier: {path}")
        fps_values.append(video_fps)

        audio_flags.append(has_audio_track(path))

        # Filtre vidéo pour normaliser la taille, les FPS et la vitesse
        video_filter_parts.append(
            f"[{idx}:v:0]scale=w={width}:h={height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
            f"fps={{fps}},setpts={1 / ratio_to_multiply_animations:.6f}*PTS[v{idx}]"
        )

    average_fps = fps if fps else (sum(fps_values) / len(fps_values))
    logger.debug(f"Utilisation des FPS cibles: {average_fps:.2f}")

    formatted_video_filters = [f.format(fps=average_fps) for f in video_filter_parts]
    video_inputs = "".join(f"[v{idx}]" for idx in range(len(video_file_paths)))

    if not any(audio_flags):
        # Cas 1: Aucune vidéo n'a de son
        logger.debug("Aucune piste audio détectée. Concaténation vidéo uniquement.")
        filter_complex = ";".join(formatted_video_filters)
        filter_complex += (
            f";{video_inputs}concat=n={len(video_file_paths)}:v=1:a=0[outv]"
        )
        map_options = ["-map", "[outv]"]
        audio_codec_options = []
    else:
        # Cas 2: Au moins une vidéo a du son (cas mixte ou toutes avec son)
        logger.debug("Pistes audio détectées. Normalisation et concaténation audio.")

        # Trouver une vidéo de référence pour les propriétés audio
        audio_ref_path = next(
            path for i, path in enumerate(video_file_paths) if audio_flags[i]
        )
        sample_rate, channel_layout = get_audio_properties(audio_ref_path)
        logger.debug(
            f"Propriétés audio de référence: {sample_rate}Hz, {channel_layout}"
        )

        durations = [get_media_duration(p) for p in video_file_paths]
        audio_filter_parts = []

        for idx, path in enumerate(video_file_paths):
            if audio_flags[idx]:
                # Cette vidéo a du son : on le normalise
                audio_filter_parts.append(
                    f"[{idx}:a:0]aformat=sample_rates={sample_rate}:channel_layouts={channel_layout},"
                    f"asetpts=PTS-STARTPTS,atempo={ratio_to_multiply_animations:.6f}[a{idx}]"
                )
            else:
                # Cette vidéo n'a pas de son : on génère du silence
                duration = durations[idx] / ratio_to_multiply_animations
                audio_filter_parts.append(
                    f"aevalsrc=exprs=0:d={duration:.6f}:r={sample_rate}:cl={channel_layout}[a{idx}]"
                )

        audio_inputs = "".join(f"[a{idx}]" for idx in range(len(video_file_paths)))
        all_filters = formatted_video_filters + audio_filter_parts

        filter_complex = ";".join(all_filters)
        filter_complex += f";{video_inputs}{audio_inputs}concat=n={len(video_file_paths)}:v=1:a=1[outv][outa]"

        map_options = ["-map", "[outv]", "-map", "[outa]"]
        audio_codec_options = ["-c:a", "aac", "-b:a", "192k"]

    cmd.extend(["-filter_complex", filter_complex])
    cmd.extend(map_options)
    cmd.extend(["-c:v", "libx264", "-crf", "23", "-preset", "fast"])
    cmd.extend(audio_codec_options)
    cmd.append(target_file_name)

    logger.debug(f"Commande FFmpeg finale: {' '.join(cmd)}")
    await _run_command(cmd)
    return target_file_name


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
