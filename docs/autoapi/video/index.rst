
video
=====

.. py:module:: video


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`Video <video.Video>`
     - Video is a class that helps to manage video files, be it a small video to be mixed or the final one.



.. list-table:: Attributes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`DEFAULT_VIDEO_TITLE <video.DEFAULT_VIDEO_TITLE>`
     - \-


Classes
-------

.. py:class:: Video(width: int = 512, height: int = 320)

   Bases: :py:obj:`abc.ABC`

   Video is a class that helps to manage video files, be it a small video to be mixed or the final one.

   - it stores metadata about itself amd possibly sub-videos
   - Video is actually really generated when you do call the build method. This is an immutable operation, i.e. once built, you cannot rebuild or change the properties of the video object.



   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`build <video.Video.build>`\ (build_settings)
        - Build in async but expose a sync interface
      * - :py:obj:`build_async <video.Video.build_async>`\ (build_settings)
        - Build the video in the child classes, unless the video is already built, in  which case
      * - :py:obj:`gather_and_run_handlers <video.Video.gather_and_run_handlers>`\ ()
        - Gather the handler chain and run it
      * - :py:obj:`generate_background_music_prompt <video.Video.generate_background_music_prompt>`\ ()
        - Get the background music prompt from the video list.
      * - :py:obj:`get_core_handlers <video.Video.get_core_handlers>`\ (build_settings)
        - Get the core handlers for the video
      * - :py:obj:`get_duration <video.Video.get_duration>`\ ()
        - Get the duration of the final video
      * - :py:obj:`get_file_name_by_state <video.Video.get_file_name_by_state>`\ (build_settings)
        - Get the file name of the video by its state
      * - :py:obj:`get_first_frame_as_image <video.Video.get_first_frame_as_image>`\ ()
        - Get the first frame of the video
      * - :py:obj:`get_last_frame_as_image <video.Video.get_last_frame_as_image>`\ ()
        - Get the last frame of the video
      * - :py:obj:`get_title <video.Video.get_title>`\ ()
        - :summarylabel:`abc` Returns the title of the video.
      * - :py:obj:`prepare_build <video.Video.prepare_build>`\ (build_settings)
        - Prepare the video for building, may be used to inject build settings for individual videos
      * - :py:obj:`run_build_core_logic_hook <video.Video.run_build_core_logic_hook>`\ (build_settings)
        - Run the core logic of the video building
      * - :py:obj:`run_post_build_actions_hook <video.Video.run_post_build_actions_hook>`\ (build_settings)
        - Post build actions hook
      * - :py:obj:`run_pre_build_actions_hook <video.Video.run_pre_build_actions_hook>`\ (build_settings)
        - Pre build actions hook
      * - :py:obj:`set_final_video_name <video.Video.set_final_video_name>`\ (output_file_name)
        - Rename the video media file to the output_file_name if not already set


   .. rubric:: Members

   .. py:method:: build(build_settings: vikit.video.video_build_settings.VideoBuildSettings = VideoBuildSettings())

      Build in async but expose a sync interface


   .. py:method:: build_async(build_settings: vikit.video.video_build_settings.VideoBuildSettings = VideoBuildSettings())
      :async:


      Build the video in the child classes, unless the video is already built, in  which case
      we just return ourselves (Video gets immutable once generated)

      This is a template method, the child classes should implement the get_handler_chain method

      :param build_settings: The settings to use for building the video
      :type build_settings: VideoBuildSettings

      :returns: The built video
      :rtype: Video


   .. py:method:: gather_and_run_handlers()
      :async:


      Gather the handler chain and run it


   .. py:method:: generate_background_music_prompt()

      Get the background music prompt from the video list.

      :returns: The background music prompt
      :rtype: str


   .. py:method:: get_core_handlers(build_settings=None)

      Get the core handlers for the video


   .. py:method:: get_duration()

      Get the duration of the final video

      :returns: The duration of the final video
      :rtype: float


   .. py:method:: get_file_name_by_state(build_settings: vikit.video.video_build_settings.VideoBuildSettings = None)

      Get the file name of the video by its state

      Shortcut method not to have to call the VideoFileName class directly


   .. py:method:: get_first_frame_as_image()
      :async:


      Get the first frame of the video


   .. py:method:: get_last_frame_as_image()
      :async:


      Get the last frame of the video


   .. py:method:: get_title()
      :abstractmethod:


      Returns the title of the video.


   .. py:method:: prepare_build(build_settings: vikit.video.video_build_settings.VideoBuildSettings) -> Video
      :async:


      Prepare the video for building, may be used to inject build settings for individual videos
      that we don't want to share with global buildsettings. For instance to generate a video
      a given way, and another video another way, all in the same composite video

      :param build_settings: The settings to use for building the video later on
      :type build_settings: VideoBuildSettings

      :returns: The current instance, prepared for building
      :rtype: Video


   .. py:method:: run_build_core_logic_hook(build_settings: vikit.video.video_build_settings.VideoBuildSettings)
      :async:


      Run the core logic of the video building

      :param build_settings: The settings to use for building the video
      :type build_settings: VideoBuildSettings


   .. py:method:: run_post_build_actions_hook(build_settings: vikit.video.video_build_settings.VideoBuildSettings)
      :async:


      Post build actions hook


   .. py:method:: run_pre_build_actions_hook(build_settings: vikit.video.video_build_settings.VideoBuildSettings)
      :async:


      Pre build actions hook

      :param build_settings: The settings to use for building the video
      :type build_settings: VideoBuildSettings


   .. py:method:: set_final_video_name(output_file_name: str)

      Rename the video media file to the output_file_name if not already set
      as the current media file.

      Today this function only works for local files.

      We fail open: in case no target file name works, we just keep the video
      as it is and where it stands. We send a warning to the logger though.

      :param output_file_name: The output file name
      :type output_file_name: str

      :returns: The video with the target file name





Attributes
----------
.. py:data:: DEFAULT_VIDEO_TITLE
   :value: 'no-title-yet'




