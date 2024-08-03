
raw_text_based_video
====================

.. py:module:: raw_text_based_video


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`RawTextBasedVideo <raw_text_based_video.RawTextBasedVideo>`
     - Generates a video from raw text prompt, i.e. very similar to calling a mainstream video generation platform.




Classes
-------

.. py:class:: RawTextBasedVideo(raw_text_prompt: str = None, title=None)

   Bases: :py:obj:`vikit.video.video.Video`

   Generates a video from raw text prompt, i.e. very similar to calling a mainstream video generation platform.
   This is currently the smallest building block available in the SDK, aimed to be used when you want more control
   over the video generation process.


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`get_core_handlers <raw_text_based_video.RawTextBasedVideo.get_core_handlers>`\ (build_settings)
        - Get the handler chain of the video. Order matters here.
      * - :py:obj:`get_title <raw_text_based_video.RawTextBasedVideo.get_title>`\ ()
        - \-
      * - :py:obj:`run_build_core_logic_hook <raw_text_based_video.RawTextBasedVideo.run_build_core_logic_hook>`\ (build_settings)
        - \-


   .. rubric:: Members

   .. py:method:: get_core_handlers(build_settings: vikit.video.video_build_settings.VideoBuildSettings) -> list[vikit.common.handler.Handler]

       Get the handler chain of the video. Order matters here.
       At this stage, we should already have the enhanced prompt and title for this video

      :param build_settings: The settings for building the video
      :type build_settings: VideoBuildSettings

       Returns:
           list: The list of handlers to use for building the video


   .. py:method:: get_title()

   .. py:method:: run_build_core_logic_hook(build_settings: vikit.video.video_build_settings.VideoBuildSettings)






