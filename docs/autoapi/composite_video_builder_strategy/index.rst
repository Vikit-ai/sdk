
composite_video_builder_strategy
================================

.. py:module:: composite_video_builder_strategy


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`CompositeVideoBuilderStrategy <composite_video_builder_strategy.CompositeVideoBuilderStrategy>`
     - Composite video builder strategy is the base class for strategies to build composite videos:




Classes
-------

.. py:class:: CompositeVideoBuilderStrategy

   Bases: :py:obj:`abc.ABC`

   Composite video builder strategy is the base class for strategies to build composite videos:

   Some strategies will target maximul quality while others will get video faster for a quick preview


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`execute <composite_video_builder_strategy.CompositeVideoBuilderStrategy.execute>`\ (composite_video, build_settings)
        - :summarylabel:`abc` Execute the composite video builder strategy


   .. rubric:: Members

   .. py:method:: execute(composite_video: CompositeVideo, build_settings: vikit.video.video_build_settings.VideoBuildSettings)
      :abstractmethod:


      Execute the composite video builder strategy

      We need to use hints as strings to prevent circular dependencies

      :param composite_video: The composite video
      :type composite_video: CompositeVideo
      :param build_settings: The build settings
      :type build_settings: VideoBuildSettings

      :returns: The composite video
      :rtype: CompositeVideo







