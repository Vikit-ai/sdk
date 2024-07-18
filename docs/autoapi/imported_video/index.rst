imported_video
==============

.. py:module:: imported_video


Classes
-------

.. autoapisummary::

   imported_video.ImportedVideo


Module Contents
---------------


.. py:class:: ImportedVideo(video_file_path: str = None)

   Bases: :py:obj:`vikit.video.video.Video`

   ImportedVideo is a simple way to generate a video based out of an existing video file


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`build <imported_video.ImportedVideo.build>`\ (build_settings)
        - Build the video
      * - :py:obj:`get_file_name_by_state <imported_video.ImportedVideo.get_file_name_by_state>`\ (build_settings)
        - Get the file name of the video
      * - :py:obj:`get_title <imported_video.ImportedVideo.get_title>`\ ()
        - Returns the title of the video.


   .. rubric:: Members

   .. py:method:: build(build_settings: vikit.video.video.VideoBuildSettings = None)

      Build the video

      Args:
          build_settings (VideoBuildSettings): The settings for building the video

      Returns:
          ImportedVideo: The built video


   .. py:method:: get_file_name_by_state(build_settings: vikit.video.video.VideoBuildSettings)

      Get the file name of the video

      Returns:
          str: The file name of the video


   .. py:method:: get_title()

      Returns the title of the video.



