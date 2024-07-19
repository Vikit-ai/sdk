
composite_video_builder_strategy_local
======================================

.. py:module:: composite_video_builder_strategy_local


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`CompositeVideoBuilderStrategyLocal <composite_video_builder_strategy_local.CompositeVideoBuilderStrategyLocal>`
     - Composite video builder strategy local is the strategy to build composite videos locally:



.. list-table:: Attributes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`executor <composite_video_builder_strategy_local.executor>`
     - \-


Classes
-------

.. py:class:: CompositeVideoBuilderStrategyLocal

   Bases: :py:obj:`vikit.video.composite_video_builder_strategy.CompositeVideoBuilderStrategy`

   Composite video builder strategy local is the strategy to build composite videos locally:

   - call API's to generate the videos and transitions
   - call ffmpeg to concatenate the videos locally using your computer resources



   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`execute <composite_video_builder_strategy_local.CompositeVideoBuilderStrategyLocal.execute>`\ (composite_video, build_settings)
        - Mix all the videos in the list: here we actually build and stitch the videos together, will take some time and resources,
      * - :py:obj:`process_videos_async <composite_video_builder_strategy_local.CompositeVideoBuilderStrategyLocal.process_videos_async>`\ (build_settings, video_list, function_to_invoke)
        - Process the videos asynchronously


   .. rubric:: Members

   .. py:method:: execute(composite_video: CompositeVideo, build_settings: vikit.video.video_build_settings.VideoBuildSettings) -> CompositeVideo

      Mix all the videos in the list: here we actually build and stitch the videos together, will take some time and resources,
      as we call external services and run video mixing locally.
      The video mixing process happens once we have all the videos to mix

      :param composite_video: The composite video
      :param build_settings: The build settings

      :returns: The composite video
      :rtype: CompositeVideo


   .. py:method:: process_videos_async(build_settings: vikit.video.video_build_settings.VideoBuildSettings, video_list, function_to_invoke)

      Process the videos asynchronously

      :param build_settings: The build settings
      :type build_settings: VideoBuildSettings
      :param video_list: The list of videos
      :type video_list: list
      :param function_to_invoke: The function to invoke
      :type function_to_invoke: function

      :returns: The list of processed videos
      :rtype: list





Attributes
----------
.. py:data:: executor



