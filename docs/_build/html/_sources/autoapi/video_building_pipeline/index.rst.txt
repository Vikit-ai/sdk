
video_building_pipeline
=======================

.. py:module:: video_building_pipeline


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`VideoBuildingPipeline <video_building_pipeline.VideoBuildingPipeline>`
     - \-




Classes
-------

.. py:class:: VideoBuildingPipeline


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`get_background_music_handlers <video_building_pipeline.VideoBuildingPipeline.get_background_music_handlers>`\ (build_settings, video)
        - Get the background music handlers
      * - :py:obj:`get_handlers <video_building_pipeline.VideoBuildingPipeline.get_handlers>`\ (video, build_settings)
        - Get the handlers for the video building pipeline, in the right order
      * - :py:obj:`get_read_aloud_prompt_handlers <video_building_pipeline.VideoBuildingPipeline.get_read_aloud_prompt_handlers>`\ (build_settings)
        - Get the read aloud prompt handlers


   .. rubric:: Members

   .. py:method:: get_background_music_handlers(build_settings: vikit.video.video_build_settings.VideoBuildSettings, video)

      Get the background music handlers


   .. py:method:: get_handlers(video, build_settings: vikit.video.video_build_settings.VideoBuildSettings)

      Get the handlers for the video building pipeline, in the right order
      - background music based on the build settings (background music)
      - read aloud prompt based on the build settings (read aloud prompt)



   .. py:method:: get_read_aloud_prompt_handlers(build_settings: vikit.video.video_build_settings.VideoBuildSettings)

      Get the read aloud prompt handlers







