
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

.. py:class:: CompositeVideo

   Bases: :py:obj:`vikit.video.video.Video`, :py:obj:`is_composite_video`

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
      * - :py:obj:`cleanse_video_list <composite_video.CompositeVideo.cleanse_video_list>`\ ()
        - Cleanse the video list by removing any empty composites videos
      * - :py:obj:`concatenate <composite_video.CompositeVideo.concatenate>`\ ()
        - Concatenate the videos for this composite
      * - :py:obj:`generate_background_music_prompt <composite_video.CompositeVideo.generate_background_music_prompt>`\ ()
        - Get the background music prompt from the video list.
      * - :py:obj:`get_children_build_settings <composite_video.CompositeVideo.get_children_build_settings>`\ ()
        - Get the  build settings for children Video
      * - :py:obj:`get_duration <composite_video.CompositeVideo.get_duration>`\ ()
        - Get the duration of the video, we recompute it everytime
      * - :py:obj:`get_title <composite_video.CompositeVideo.get_title>`\ ()
        - Get the title of the video, we recompute it everytime
      * - :py:obj:`is_composite_video <composite_video.CompositeVideo.is_composite_video>`\ ()
        - \-
      * - :py:obj:`run_build_core_logic_hook <composite_video.CompositeVideo.run_build_core_logic_hook>`\ (build_settings)
        - Mix all the videos in the list: here we actually build and stitch the videos together,
      * - :py:obj:`run_post_build_actions_hook <composite_video.CompositeVideo.run_post_build_actions_hook>`\ (build_settings)
        - \-
      * - :py:obj:`run_pre_build_actions_hook <composite_video.CompositeVideo.run_pre_build_actions_hook>`\ (build_settings)
        - \-
      * - :py:obj:`update_metadata_post_building <composite_video.CompositeVideo.update_metadata_post_building>`\ ()
        - Update the metadata post building


   .. rubric:: Members

   .. py:method:: append_video(video: vikit.video.video.Video)

      Append a video to the list of videos to be mixed

      params:
          video: The video to be appended

      :returns: The current object
      :rtype: self


   .. py:method:: cleanse_video_list()

      Cleanse the video list by removing any empty composites videos


   .. py:method:: concatenate()
      :async:


      Concatenate the videos for this composite


   .. py:method:: generate_background_music_prompt()

      Get the background music prompt from the video list.

      :returns: The background music prompt
      :rtype: str


   .. py:method:: get_children_build_settings()

      Get the  build settings for children Video


   .. py:method:: get_duration()

      Get the duration of the video, we recompute it everytime
      as the duration of the video can change if we add or remove videos


   .. py:method:: get_title()

      Get the title of the video, we recompute it everytime
      as the title of the video can change if we add or remove videos


   .. py:method:: is_composite_video()

   .. py:method:: run_build_core_logic_hook(build_settings=VideoBuildSettings())
      :async:


      Mix all the videos in the list: here we actually build and stitch the videos together,
      will take some time and resources as we call external services and run video mixing locally.

      Warning: order is very importamnt here, and the first pass is supposed to happen from the rootcomposite levels

      Today we do generate the videos so the first ones are the ones that will be used to generate the final video
      This requires a specific order, and generating videos ahad of time won't work unless you take care
      of building the videos in the child composite video list first.

      params:
          build_settings: The settings to be used for the build

      :returns: The current object
      :rtype: self


   .. py:method:: run_post_build_actions_hook(build_settings: vikit.video.video_build_settings.VideoBuildSettings)
      :async:


   .. py:method:: run_pre_build_actions_hook(build_settings: vikit.video.video_build_settings.VideoBuildSettings)
      :async:


   .. py:method:: update_metadata_post_building()

      Update the metadata post building







