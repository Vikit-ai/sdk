import os

from vikit.postprocessing.logo.model import LogoConfig
from vikit.postprocessing.subtitles.model import SubtitleConfig

_CUR_DIR = os.path.dirname(os.path.abspath(__file__))


def _local_resource(filename: str):
    return os.path.join(_CUR_DIR, filename)


LUMA_MP4 = _local_resource("luma.mp4")
LUMA_WITH_LOGO_MP4 = _local_resource("luma_with_logo.mp4")
TRANSPARENT_VIKIT_LOGO_BLACK_PNG = _local_resource("transparent_vikit_logo_black.png")
IMAGE_SVG = _local_resource("svg_image.svg")
WHITE_BACKGROUND_VIKIT_LOGO_BLACK_PNG = _local_resource(
    "white_background_vikit_logo_black.png"
)
IMAGE_PROMPT = _local_resource("image_prompt.jpeg")
VIKIT_PITCH_MP4 = _local_resource("vikit_pitch.mp4")
MARCHAND_360P_MP4 = _local_resource("marchand_360p.mp4")
MARCHAND_CHUNK_SRT = _local_resource("marchand_chunk.srt")
QUOTIDIEN_360P_MP4 = _local_resource("quotidien_360p.mp4")
QUOTIDIEN_CHUNK_SRT = _local_resource("quotidien_chunk.srt")
PODCAST_SERENITY_MUSIC = _local_resource("PodcastSerenity.mp3")

RANCHO_FONT = _local_resource("fonts/rancho.ttf")

OUTPUT_VIDEO_WITH_SUBTITLES_NAME = "vikit_pitch_with_subtitles.mp4"

VALID_SUBTITLE_CONFIG = SubtitleConfig(
    input_video_path=MARCHAND_360P_MP4,
    output_video_name=OUTPUT_VIDEO_WITH_SUBTITLES_NAME,
    subtitle_srt_path=MARCHAND_CHUNK_SRT,
    text_color="white",
    highlight_color="yellow",
    bg_color=(0, 0, 0),
    text_font="Arial",
    font_size_px=18,
    highlight_opacity=0.9,
    subtitle_style="static_block",
)

OUTPUT_VIDEO_WITH_LOGO_NAME = "vikit_pitch_with_logo.mp4"

VALID_LOGO_CONFIG = LogoConfig(
    input_video_path=VIKIT_PITCH_MP4,
    output_video_name=OUTPUT_VIDEO_WITH_LOGO_NAME,
    logo=TRANSPARENT_VIKIT_LOGO_BLACK_PNG,
    position="top_left",
    margin_pix=30,
    opacity=0.9,
    height_size_px=100,
    logo_height_percentage=9,
)
