video
=====

.. py:module:: video


Classes
-------

.. autoapisummary::

   video.Video


Module Contents
---------------


.. py:class:: Video(width: int = 512, height: int = 320)

   Bases: :py:obj:`abc.ABC`

   Video is a class that helps to manage video files, be it a small video to be mixed or the final one.

   - it stores metadata about itself amd possibly subvideos
   - Video is actually really generated when you do call the build method. This is an immutable operation, i.e. once built, you cannot rebuild or change the properties of the video object.



   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`build <video.Video.build>`\ (build_settings)
        - :summarylabel:`abc` Build the video in the child classes, unless the video is already built, in  which case
      * - :py:obj:`get_duration <video.Video.get_duration>`\ ()
        - Get the duration of the final video
      * - :py:obj:`get_file_name_by_state <video.Video.get_file_name_by_state>`\ (build_settings, metadata, video_type)
        - Get the file name of the video depending on the current metadata / vide state
      * - :py:obj:`get_first_frame_as_image <video.Video.get_first_frame_as_image>`\ ()
        - Get the first frame of the video
      * - :py:obj:`get_last_frame_as_image <video.Video.get_last_frame_as_image>`\ ()
        - Get the last frame of the video
      * - :py:obj:`get_title <video.Video.get_title>`\ ()
        - :summarylabel:`abc` Returns the title of the video.


   .. rubric:: Members

   .. py:method:: build(build_settings: vikit.video.video_build_settings.VideoBuildSettings = None)
      :abstractmethod:


      Build the video in the child classes, unless the video is already built, in  which case
      we just return ourseleves (Video gets immutable once generated)

      Args:
          build_settings (VideoBuildSettings): The settings to use for building the video

      Returns:
          Video: The built video



   .. py:method:: get_duration()

      Get the duration of the final video

      Returns:
          float: The duration of the final video


   .. py:method:: get_file_name_by_state(build_settings: vikit.video.video_build_settings.VideoBuildSettings, metadata: vikit.video.video_metadata.VideoMetadata = None, video_type: str = None)

      Get the file name of the video depending on the current metadata / vide state

      params:
          build_settings (VideoBuildSettings): used to gather build contextual information
          metadata (VideoMetadata): The metadata to use for generating the file name
          video_type (str): The type of the video

      Returns:
          str: The file name of the video


   .. py:method:: get_first_frame_as_image()

      Get the first frame of the video


   .. py:method:: get_last_frame_as_image()

      Get the last frame of the video


   .. py:method:: get_title()
      :abstractmethod:


      Returns the title of the video.



