
imported_video
==============

.. py:module:: imported_video


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`ImportedVideo <imported_video.ImportedVideo>`
     - ImportedVideo is a simple way to generate a video based out of an existing video file




Classes
-------

.. py:class:: ImportedVideo(video_file_path: str = None)

   Bases: :py:obj:`vikit.video.video.Video`

   ImportedVideo is a simple way to generate a video based out of an existing video file


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`get_title <imported_video.ImportedVideo.get_title>`\ ()
        - Returns the title of the video.
      * - :py:obj:`prepare_build_hook <imported_video.ImportedVideo.prepare_build_hook>`\ (build_settings)
        - Prepare the video build


   .. rubric:: Members

   .. py:method:: get_title()

      Returns the title of the video.


   .. py:method:: prepare_build_hook(build_settings: vikit.video.video_build_settings.VideoBuildSettings)
      :async:


      Prepare the video build

      :param build_settings: The build settings
      :type build_settings: VideoBuildSettings

      :returns: The video build order
      :rtype: list







