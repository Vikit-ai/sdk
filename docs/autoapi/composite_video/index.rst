
composite_video
===============

.. py:module:: composite_video


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`CompositeVideo <composite_video.CompositeVideo>`
     - Composite made from the collection of videos that need to be generated altogether, as a consistent block




Classes
-------

.. py:class:: CompositeVideo(target_file_name=None)

   Bases: :py:obj:`vikit.video.video.Video`

   Composite made from the collection of videos that need to be generated altogether, as a consistent block
   It could be a final video or intermediate  composing specific scenes of the final video.

   Composite video can include other composite videos, and so on, to build a tree of videos to be generated


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`append_video <composite_video.CompositeVideo.append_video>`\ (video)
        - Append a video to the list of videos to be mixed
      * - :py:obj:`build <composite_video.CompositeVideo.build>`\ (build_settings, building_strategy)
        - Mix all the videos in the list: here we actually build and stitch the videos together, will take some time and resources,
      * - :py:obj:`get_duration <composite_video.CompositeVideo.get_duration>`\ ()
        - Get the duration of the video, we recompute it everytime
      * - :py:obj:`get_file_name_by_state <composite_video.CompositeVideo.get_file_name_by_state>`\ (build_settings)
        - Get the target / expected file name for the composite video depending on its state
      * - :py:obj:`get_title <composite_video.CompositeVideo.get_title>`\ ()
        - Get the title of the video, we recompute it everytime


   .. rubric:: Members

   .. py:method:: append_video(video: vikit.video.video.Video = None)

      Append a video to the list of videos to be mixed

      params:
          video: The video to be appended

      :returns: The current object
      :rtype: self


   .. py:method:: build(build_settings=VideoBuildSettings(), building_strategy: vikit.video.composite_video_builder_strategy.CompositeVideoBuilderStrategy = None)

      Mix all the videos in the list: here we actually build and stitch the videos together, will take some time and resources,
      as we call external services and run video mixing locally.

      The actual algorithm depends on the provided strategy (local, cloud, etc.)

      :param build_settings: The settings to be used for the build
      :param building_strategy: The strategy to be used for the build

      :returns: The current object
      :rtype: self


   .. py:method:: get_duration()

      Get the duration of the video, we recompute it everytime
      as the duration of the video can change if we add or remove videos


   .. py:method:: get_file_name_by_state(build_settings: vikit.video.video.VideoBuildSettings = None)

      Get the target / expected file name for the composite video depending on its state
      State is build progressively from Instantiation to the final build, where steps like
      adding music or audio prompt are carried out

      params:
          build_settings: The settings to be used for the build

      :returns: The target file name
      :rtype: str


   .. py:method:: get_title()

      Get the title of the video, we recompute it everytime
      as the title of the video can change if we add or remove videos







