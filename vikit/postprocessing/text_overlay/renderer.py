import numpy as np
from moviepy.editor import CompositeVideoClip, ImageClip, TextClip, VideoFileClip
from PIL import Image, ImageDraw

from vikit.common.video_tools import write_videofile
from vikit.postprocessing.text_overlay.model import TextOverlay


def render_text_overlay(
    src_video_path: str,
    dst_video_path: str,
    text_overlay: TextOverlay,
):
    video = VideoFileClip(src_video_path, fps_source="fps")

    # Generate 1 clip for each of the lines.
    line_clips = []

    overlay_width_px = 0  # max line width, computed in the for-loop
    overlay_height_px = 0  # running total computed in the for-loop
    for idx, line in enumerate(text_overlay.lines):
        line_style = line.line_style_override or text_overlay.line_style

        # Render the text.
        text_clip = TextClip(
            line.text,
            font=line_style.font_path,
            fontsize=line_style.font_size_pt,
            color=line_style.text_color,
        )
        text_clip = text_clip.set_position("center")

        # Create the background box by drawing a rounded rectangle on a transparent
        # image.
        text_width_px, text_height_px = text_clip.size
        bg_width_px = text_width_px + line_style.bg_padding_px
        bg_height_px = text_height_px + line_style.bg_padding_px

        bg_image = Image.new("RGBA", (bg_width_px, bg_height_px), (0, 0, 0, 0))
        draw = ImageDraw.Draw(bg_image)
        draw.rounded_rectangle(
            (0, 0, bg_width_px, bg_height_px),
            line_style.bg_corner_radius_px,
            fill=line_style.bg_color,
        )
        bg_clip = ImageClip(np.array(bg_image))

        # Insert the specified line spacing before the next line.
        if idx > 0:
            overlay_height_px += line_style.line_spacing_px

        # Combine the background box and the text.
        line_composite_clip = CompositeVideoClip([bg_clip, text_clip]).set_position(
            ("center", overlay_height_px)
        )
        line_clips.append(line_composite_clip)
        line_composite_width_px, line_composite_height_px = line_composite_clip.size
        overlay_width_px = max(overlay_width_px, line_composite_width_px)
        overlay_height_px += line_composite_height_px

    # Assemble all line clips into a single composite.
    video_width_px, video_height_px = video.size

    h_offset_px = text_overlay.position.h_offset_px if text_overlay.position else 0
    overlay_position_x = video_width_px / 2 - overlay_width_px / 2 + h_offset_px

    v_offset_px = text_overlay.position.v_offset_px if text_overlay.position else 0
    overlay_position_y = video_height_px / 2 - overlay_height_px / 2 + v_offset_px

    start_time_sec = text_overlay.timing.start_time_sec
    end_time_sec = min(video.duration, text_overlay.timing.end_time_sec)

    overlay_clip: CompositeVideoClip = (
        CompositeVideoClip(line_clips, size=(overlay_width_px, overlay_height_px))
        .set_position((overlay_position_x, overlay_position_y))
        .set_start(start_time_sec)
        .set_duration(end_time_sec - start_time_sec)
    )

    # Assemble and render the final composite video.
    final_clip = CompositeVideoClip([video, overlay_clip])
    write_videofile(final_clip, dst_video_path, fps=video.fps)
