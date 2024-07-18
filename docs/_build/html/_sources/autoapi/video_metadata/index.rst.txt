video_metadata
==============

.. py:module:: video_metadata


Classes
-------

.. autoapisummary::

   video_metadata.VideoMetadata


Module Contents
---------------


.. py:class:: VideoMetadata(id: uuid = None, title=None, duration=None, width: int = None, height: int = None, top_parent_id=None, is_video_generated=False, is_reencoded=False, is_interpolated=False, is_bg_music_applied=False, is_subtitle_audio_applied=False, is_bg_music_generated=None, is_prompt_read_aloud=False, **custom_metadata)

   Hybrid DTO class for storing video metadata.

   Attributes:
   title (str): Title of the video.
   duration (int): Duration of the video in seconds.
   height (str): height of the video.
   width (str): width of the video.
   is_video_generated (bool): Whether the video is generated.
   is_reencoded (bool): Whether the video is reencoded.
   is_interpolated (bool): Whether the video is interpolated.
   is_bg_music_applied (bool): Whether the background music is applied.
   is_bg_music_generated (bool): Whether the background music is generated.
   is_subtitle_audio_applied (bool): Whether the subtitle audio is applied, useful for music tracks
   is_prompt_read_aloud (bool): Whether the prompt text is read aloud by synthetic voice.

   extra_metadata (dict): Extra metadata for the video.



