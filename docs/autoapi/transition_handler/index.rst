
transition_handler
==================

.. py:module:: transition_handler


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`VideoBuildingHandlerTransition <transition_handler.VideoBuildingHandlerTransition>`
     - \-




Classes
-------

.. py:class:: VideoBuildingHandlerTransition

   Bases: :py:obj:`vikit.common.handler.Handler`


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`execute_async <transition_handler.VideoBuildingHandlerTransition.execute_async>`\ (video)
        - Process the video generation binaries: we actually do ask the video to build itself


   .. rubric:: Members

   .. py:method:: execute_async(video: vikit.video.video.Video)
      :async:


      Process the video generation binaries: we actually do ask the video to build itself
      as a video binary (typically an MP4 generated from Gen AI, hosted behind an API),
      or to compose from its inner videos in case of a child composite video

      :param args: The arguments: video, build_settings, video.media_url, target_file_name

      :returns: The composite video
      :rtype: CompositeVideo







