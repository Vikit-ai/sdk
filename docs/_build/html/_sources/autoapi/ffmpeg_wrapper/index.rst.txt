
ffmpeg_wrapper
==============

.. py:module:: ffmpeg_wrapper


Overview
--------


.. list-table:: Function
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`concatenate_videos <ffmpeg_wrapper.concatenate_videos>`\ (input_file, target_file_name, ratioToMultiplyAnimations, bias)
     - Concatenate all the videos in the list using a concatenation file
   * - :py:obj:`convert_as_mp3_file <ffmpeg_wrapper.convert_as_mp3_file>`\ (fileName, target_file_name)
     - Save the incoming audio file to a regular mp3 file with a standardised filename
   * - :py:obj:`extract_audio_slice <ffmpeg_wrapper.extract_audio_slice>`\ (audiofile_path, start, end, target_file_name)
     - Extract a slice of the audio file using ffmpeg
   * - :py:obj:`get_media_duration <ffmpeg_wrapper.get_media_duration>`\ (input_video_path)
     - Get the duration of a media file.
   * - :py:obj:`has_audio_track <ffmpeg_wrapper.has_audio_track>`\ (video_path)
     - Check if the video has an audio track
   * - :py:obj:`merge_audio <ffmpeg_wrapper.merge_audio>`\ (media_url, audio_file_path, audio_file_relative_volume, target_file_name)
     - Merge audio with the video
   * - :py:obj:`reencode_video <ffmpeg_wrapper.reencode_video>`\ (params)
     - Reencode the video, doing this for imported video that might not concatenate well




Functions
---------
.. py:function:: concatenate_videos(input_file: str, target_file_name=None, ratioToMultiplyAnimations=1, bias=0.33)

   Concatenate all the videos in the list using a concatenation file

   :param input_file: The path to the input file
   :type input_file: str
   :param target_file_name: The target file name
   :type target_file_name: str
   :param ratioToMultiplyAnimations: The ratio to multiply animations
   :type ratioToMultiplyAnimations: int
   :param bias: The bias to add to the ratio for the sound to be in sync with video frames
   :type bias: int

   :returns: The path to the concatenated video file
   :rtype: str


.. py:function:: convert_as_mp3_file(fileName, target_file_name: str)

   Save the incoming audio file to a regular mp3 file with a standardised filename

   :param fileName: The path to the audio file to convert
   :type fileName: str

   :returns: The path to the converted audio file
   :rtype: str


.. py:function:: extract_audio_slice(audiofile_path: str, start: float = 0, end: float = 1, target_file_name: str = None)

   Extract a slice of the audio file using ffmpeg

   :param start: The start of the slice
   :type start: int
   :param end: The end of the slice
   :type end: int
   :param audiofile_path: The path to the audio file
   :type audiofile_path: str
   :param target_file_name: the target file name

   :returns: The path to the extracted audio slice
   :rtype: str


.. py:function:: get_media_duration(input_video_path)

   Get the duration of a media file.

   :param input_video_path: The path to the input video file.
   :type input_video_path: str

   :returns: The duration of the media file in seconds.
   :rtype: float


.. py:function:: has_audio_track(video_path)

   Check if the video has an audio track

   :param video_path: The path to the video file
   :type video_path: str

   :returns: True if the video has an audio track, False otherwise
   :rtype: bool


.. py:function:: merge_audio(media_url: str, audio_file_path: str, audio_file_relative_volume: float = None, target_file_name=None)

   Merge audio with the video

   :param media_url: The media url to merge
   :type media_url: str
   :param audio_file_path: The audio file path to merge
   :type audio_file_path: str
   :param audio_file_relative_volume: The relative volume of the audio file
   :type audio_file_relative_volume: float
   :param target_file_name: The target file name
   :type target_file_name: str

   :returns: The merged audio file path
   :rtype: str


.. py:function:: reencode_video(params)

   Reencode the video, doing this for imported video that might not concatenate well
   with generated ones or among themselves

   :param params: The parameters to reencode the video
   :type params: tuple
   :param video:
   :param build_settings:
   :param video.media_url:

   :returns: The reencoded video
   :rtype: Video





