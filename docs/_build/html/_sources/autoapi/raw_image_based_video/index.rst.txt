
raw_image_based_video
=====================

.. py:module:: raw_image_based_video


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`RawImageBasedVideo <raw_image_based_video.RawImageBasedVideo>`
     - Generates a video from raw image prompt




Classes
-------

.. py:class:: RawImageBasedVideo(title: str = None, raw_image_prompt: str = None)

   Bases: :py:obj:`vikit.video.video.Video`

   Generates a video from raw image prompt


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`get_core_handlers <raw_image_based_video.RawImageBasedVideo.get_core_handlers>`\ (build_settings)
        - Get the handler chain of the video. Order matters here.
      * - :py:obj:`get_duration <raw_image_based_video.RawImageBasedVideo.get_duration>`\ ()
        - \-
      * - :py:obj:`get_title <raw_image_based_video.RawImageBasedVideo.get_title>`\ ()
        - \-
      * - :py:obj:`run_build_core_logic_hook <raw_image_based_video.RawImageBasedVideo.run_build_core_logic_hook>`\ (build_settings)
        - \-


   .. rubric:: Members

   .. py:method:: get_core_handlers(build_settings) -> list[vikit.common.handler.Handler]

       Get the handler chain of the video. Order matters here.
       At this stage, we should already have the enhanced prompt and title for this video

      :param build_settings: The settings for building the video
      :type build_settings: VideoBuildSettings

       Returns:
           list: The list of handlers to use for building the video


   .. py:method:: get_duration()

   .. py:method:: get_title()

   .. py:method:: run_build_core_logic_hook(build_settings: vikit.video.video_build_settings.VideoBuildSettings)






