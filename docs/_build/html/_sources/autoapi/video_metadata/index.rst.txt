
video_metadata
==============

.. py:module:: video_metadata


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`VideoMetadata <video_metadata.VideoMetadata>`
     - Hybrid DTO class for storing video metadata.




Classes
-------

.. py:class:: VideoMetadata(id: uuid = None, temp_id=None, title=None, duration=None, width: int = None, height: int = None, is_video_built=False, is_reencoded=False, is_interpolated=False, is_bg_music_applied=False, is_subtitle_audio_applied=False, is_bg_music_generated=None, is_default_bg_music_applied=False, is_prompt_read_aloud=False, media_url=None, **custom_metadata)

   Hybrid DTO class for storing video metadata.

   Attributes:
   id (uuid): Unique identifier of the video.
   temp_id (str): Temporary identifier of the video, used when it was being built
   title (str): Title of the video.
   duration (int): Duration of the video in seconds.
   height (str): height of the video.
   width (str): width of the video.
   is_video_built (bool): Whether the video is generated.
   is_reencoded (bool): Whether the video is reencoded.
   is_interpolated (bool): Whether the video is interpolated.
   is_bg_music_applied (bool): Whether the background music is applied.
   is_bg_music_generated (bool): Whether the background music is generated.
   is_subtitle_audio_applied (bool): Whether the subtitle audio is applied, useful for music tracks
   is_prompt_read_aloud (bool): Whether the prompt text is read aloud by synthetic voice.

   extra_metadata (dict): Extra metadata for the video.







