from loguru import logger
from moviepy.editor import VideoClip

MINIMUM_RESOLUTION_THRESHOLD = 720
DEFAULT_BITRATE = "14000k"


def write_videofile(
    video: VideoClip, output_path: str, fps: float, verbose: bool = False
):
    """
    Saves the specified clip to a file in the default Vikit video format.

    Args:
      - video (VideoClip): The video clip to write.
      - output_path (str): Path of the video file to write.
      - fps (float): Number of frames per second in the video file to write.
      - verbose (bool): Whether to generate verbose logs. Defaults to False.
    """
    kwargs = {
        "codec": "libx264",
        "audio_codec": "aac",
        "fps": fps,
        "logger": "bar" if verbose else None,
    }

    if max(video.size) < MINIMUM_RESOLUTION_THRESHOLD:
        kwargs["bitrate"] = DEFAULT_BITRATE

    video.write_videofile(output_path, **kwargs)


def resize_video_clip(video: VideoClip, short_edge_length_px: int) -> VideoClip:
    """
    Resizes the input video to the specified short edge length in pixels.

    The resized video will have a short edge of the specified target length
    (short_edge_length_px) and the long edge will be scaled proportionally so that the
    video's aspect ratio is maintained.

    Example: An input video with dimensions 1920x1080 will be resized to 1280x720 if the
    short_edge_length_px is set to 720.

    Args:
      - video (VideoClip): The video to resize.
      - short_edge_length_px: The target length of the short edge in pixels.

    Returns:
      The resized video if resizing was necessary, the input video otherwise.
    """
    original_width, original_height = video.size
    original_short_edge_length_px = min(original_width, original_height)

    resize_factor = short_edge_length_px / original_short_edge_length_px

    new_width = int(original_width * resize_factor)
    new_height = int(original_height * resize_factor)

    # Ensure that the width and height are even numbers, otherwise ffmpeg will
    # use a non-standard pixel format which causes some video players (e.g.
    # QuickTime Player) to consider the video files as corrupt.
    new_width = new_width if new_width % 2 == 0 else new_width - 1
    new_height = new_height if new_height % 2 == 0 else new_height - 1

    logger.debug(
        f"Resizing video from {original_width}x{original_height} to "
        f"{new_width}x{new_height}"
    )

    if (new_width, new_height) == (original_width, original_height):
        return video

    resized_video = video.resize((new_width, new_height))
    return resized_video
