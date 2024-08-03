
config
======

.. py:module:: config


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`singletons <config.singletons>`
     - A class to hold singletons


.. list-table:: Function
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`get_cleanup_tempfiles <config.get_cleanup_tempfiles>`\ ()
     - Whether to cleanup temporary files or not. By default we set it to False
   * - :py:obj:`get_cloud_bucket_url <config.get_cloud_bucket_url>`\ ()
     - The cloud storage bucket where final videos are stored
   * - :py:obj:`get_default_background_music <config.get_default_background_music>`\ ()
     - \-
   * - :py:obj:`get_elevenLabs_url <config.get_elevenLabs_url>`\ ()
     - \-
   * - :py:obj:`get_initial_audio_file_name <config.get_initial_audio_file_name>`\ ()
     - The file name of the user provided or llm generated audio file
   * - :py:obj:`get_nb_retries_http_calls <config.get_nb_retries_http_calls>`\ ()
     - \-
   * - :py:obj:`get_nb_subs_per_video <config.get_nb_subs_per_video>`\ ()
     - The number of subtitles to generate per video
   * - :py:obj:`get_nb_words_per_subtitle <config.get_nb_words_per_subtitle>`\ ()
     - \-
   * - :py:obj:`get_prompt_mp3_file_name <config.get_prompt_mp3_file_name>`\ ()
     - The name of the mp3 file either converted from user  or
   * - :py:obj:`get_seconds_per_word <config.get_seconds_per_word>`\ ()
     - \-
   * - :py:obj:`get_sub_audio_for_subtitle_prefix <config.get_sub_audio_for_subtitle_prefix>`\ ()
     - The prefix for the file name of the audio file that will be used for the subtitles video
   * - :py:obj:`get_subtitles_default_file_name <config.get_subtitles_default_file_name>`\ ()
     - The default name used to save the subtitles file in the working directory
   * - :py:obj:`get_subtitles_min_duration <config.get_subtitles_min_duration>`\ ()
     - \-
   * - :py:obj:`get_videho_email_contact <config.get_videho_email_contact>`\ ()
     - \-
   * - :py:obj:`get_video_length_per_subtitle <config.get_video_length_per_subtitle>`\ ()
     - The length of the video generated for each subtitle is currently directly
   * - :py:obj:`get_video_list_file_name <config.get_video_list_file_name>`\ ()
     - The file name of the list of videos files to mix with ffmpeg


.. list-table:: Attributes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`dir_path <config.dir_path>`
     - \-
   * - :py:obj:`env_file <config.env_file>`
     - \-


Classes
-------

.. py:class:: singletons

   A class to hold singletons


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`get_process_executor <config.singletons.get_process_executor>`\ ()
        - :summarylabel:`static` The process executor to use for parallel processing


   .. rubric:: Members

   .. py:method:: get_process_executor()
      :staticmethod:


      The process executor to use for parallel processing




Functions
---------
.. py:function:: get_cleanup_tempfiles() -> bool

   Whether to cleanup temporary files or not. By default we set it to False
   as we prefer to keep the files for debugging purposes or to train future models,
   or even reuse the produced sub videos


.. py:function:: get_cloud_bucket_url()

   The cloud storage bucket where final videos are stored


.. py:function:: get_default_background_music() -> str

.. py:function:: get_elevenLabs_url() -> str

.. py:function:: get_initial_audio_file_name()

   The file name of the user provided or llm generated audio file


.. py:function:: get_nb_retries_http_calls() -> int

.. py:function:: get_nb_subs_per_video() -> int

   The number of subtitles to generate per video


.. py:function:: get_nb_words_per_subtitle() -> int

.. py:function:: get_prompt_mp3_file_name() -> str

   The name of the mp3 file either converted from user  or
   generated using an llm and that we use to extract subtitles from the video


.. py:function:: get_seconds_per_word() -> float

.. py:function:: get_sub_audio_for_subtitle_prefix()

   The prefix for the file name of the audio file that will be used for the subtitles video


.. py:function:: get_subtitles_default_file_name() -> str

   The default name used to save the subtitles file in the working directory
   It is typically build from smaller subtitles generated for subvideos


.. py:function:: get_subtitles_min_duration() -> int

.. py:function:: get_videho_email_contact() -> str

.. py:function:: get_video_length_per_subtitle() -> int

   The length of the video generated for each subtitle is currently directly
   linked to the maximum anmount of time allowed by videcrafter


.. py:function:: get_video_list_file_name()

   The file name of the list of videos files to mix with ffmpeg



Attributes
----------
.. py:data:: dir_path

.. py:data:: env_file



