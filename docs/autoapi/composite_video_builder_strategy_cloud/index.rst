composite_video_builder_strategy_cloud
======================================

.. py:module:: composite_video_builder_strategy_cloud


Classes
-------

.. autoapisummary::

   composite_video_builder_strategy_cloud.CompositeVideoBuilderStrategyCloud


Module Contents
---------------


.. py:class:: CompositeVideoBuilderStrategyCloud

   Bases: :py:obj:`vikit.video.composite_video_builder_strategy.CompositeVideoBuilderStrategy`


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`execute <composite_video_builder_strategy_cloud.CompositeVideoBuilderStrategyCloud.execute>`\ (composite_video, build_settings)
        - :summarylabel:`abc` Mix all the videos in the list: here we actually build and stitch the videos together, will take some time and resources,


   .. rubric:: Members

   .. py:method:: execute(composite_video: CompositeVideo, build_settings: vikit.video.video_build_settings.VideoBuildSettings) -> CompositeVideo
      :abstractmethod:


      Mix all the videos in the list: here we actually build and stitch the videos together, will take some time and resources,
      as we call external services and run video mixing locally.
      The video mixing process happens once we have all the videos to mix

      Args:
          composite_video: The composite video
          build_settings: The build settings

      Returns:
          root_composite_video: a built composite video



