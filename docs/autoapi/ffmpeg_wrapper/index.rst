ffmpeg_wrapper
==============

.. py:module:: ffmpeg_wrapper


Functions
---------

.. autoapisummary::

   ffmpeg_wrapper.concatenate_videos
   ffmpeg_wrapper.convert_as_mp3_file
   ffmpeg_wrapper.extract_audio_slice
   ffmpeg_wrapper.get_media_duration
   ffmpeg_wrapper.has_audio_track
   ffmpeg_wrapper.merge_audio
   ffmpeg_wrapper.reencode_video


Module Contents
---------------

.. py:function:: concatenate_videos(input_file: str, target_file_name=None, ratioToMultiplyAnimations=1, bias=0.33)

   Concatenate all the videos in the list using a concatenation file

   Args:
       input_file (str): The path to the input file
       target_file_name (str): The target file name
       ratioToMultiplyAnimations (int): The ratio to multiply animations
       bias (int): The bias to add to the ratio for the sound to be in sync with video frames

   Returns:
       str: The path to the concatenated video file


.. py:function:: convert_as_mp3_file(fileName, target_file_name: str)

   Save the incoming audio file to a regular mp3 file with a standardised filename

   Args:

       fileName (str): The path to the audio file to convert

   Returns:
       str: The path to the converted audio file


.. py:function:: extract_audio_slice(audiofile_path: str, start: float = 0, end: float = 1, target_file_name: str = None)

   Extract a slice of the audio file using ffmpeg

   Args:
       start (int): The start of the slice
       end (int): The end of the slice
       audiofile_path (str): The path to the audio file
       target_file_name : the target file name

   Returns:
       str: The path to the extracted audio slice


.. py:function:: get_media_duration(input_video_path)

   Get the duration of a media file.

   Args:
       input_video_path (str): The path to the input video file.

   Returns:
       float: The duration of the media file in seconds.


.. py:function:: has_audio_track(video_path)

   Check if the video has an audio track

   Args:
       video_path (str): The path to the video file

   Returns:
       bool: True if the video has an audio track, False otherwise



.. py:function:: merge_audio(media_url: str, audio_file_path: str, audio_file_relative_volume: float = None, target_file_name=None)

   Merge audio with the video

   Args:
       media_url (str): The media url to merge
       audio_file_path (str): The audio file path to merge
       audio_file_relative_volume (float): The relative volume of the audio file
       target_file_name (str): The target file name

   Returns:
       str: The merged audio file path



.. py:function:: reencode_video(params)

   Reencode the video, doing this for imported video that might not concatenate well
   with generated ones or among themselves

   Args:
       params (tuple): The parameters to reencode the video
       video, build_settings, video.media_url

   Returns:
       Video: The reencoded video


