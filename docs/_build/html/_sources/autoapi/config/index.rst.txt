config
======

.. py:module:: config


Attributes
----------

.. autoapisummary::

   config.dir_path
   config.env_file


Functions
---------

.. autoapisummary::

   config.get_default_background_music
   config.get_elevenLabs_url
   config.get_videho_email_contact
   config.get_nb_retries_http_calls
   config.get_prompt_mp3_file_name
   config.get_subtitles_min_duration
   config.get_nb_words_per_subtitle
   config.get_seconds_per_word
   config.get_video_length_per_subtitle
   config.get_nb_subs_per_video
   config.get_subtitles_default_file_name
   config.get_cleanup_tempfiles
   config.get_sub_audio_for_subtitle_prefix
   config.get_initial_audio_file_name
   config.get_video_list_file_name
   config.get_cloud_bucket_url


Module Contents
---------------

.. py:data:: dir_path

.. py:data:: env_file

.. py:function:: get_default_background_music() -> str

.. py:function:: get_elevenLabs_url() -> str

.. py:function:: get_videho_email_contact() -> str

.. py:function:: get_nb_retries_http_calls() -> int

.. py:function:: get_prompt_mp3_file_name() -> str

   The name of the mp3 file either converted from user  or
   generated using an llm and that we use to extract subtitles from the video


.. py:function:: get_subtitles_min_duration() -> int

.. py:function:: get_nb_words_per_subtitle() -> int

.. py:function:: get_seconds_per_word() -> float

.. py:function:: get_video_length_per_subtitle() -> int

   The length of the video generated for each subtitle is currently directly
   linked to the maximum anmount of time allowed by videcrafter


.. py:function:: get_nb_subs_per_video() -> int

   The number of subtitles to generate per video


.. py:function:: get_subtitles_default_file_name() -> str

   The default name used to save the subtitles file in the working directory
   It is typically build from smaller subtitles generated for subvideos


.. py:function:: get_cleanup_tempfiles() -> bool

   Whether to cleanup temporary files or not. By default we set it to False
   as we prefer to keep the files for debugging purposes or to train future models,
   or even reuse the produced sub videos


.. py:function:: get_sub_audio_for_subtitle_prefix()

   The prefix for the file name of the audio file that will be used for the subtitles video


.. py:function:: get_initial_audio_file_name()

   The file name of the user provided or llm generated audio file


.. py:function:: get_video_list_file_name()

   The file name of the list of videos files to mix with ffmpeg


.. py:function:: get_cloud_bucket_url()

   The cloud storage bucket where final videos are stored


