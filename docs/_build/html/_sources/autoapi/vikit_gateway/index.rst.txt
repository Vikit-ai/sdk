
vikit_gateway
=============

.. py:module:: vikit_gateway


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`VikitGateway <vikit_gateway.VikitGateway>`
     - A Gateway to interact with the Vikit API



.. list-table:: Attributes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`KEYWORDS_FORMAT_PROMPT <vikit_gateway.KEYWORDS_FORMAT_PROMPT>`
     - \-
   * - :py:obj:`http_timeout <vikit_gateway.http_timeout>`
     - \-
   * - :py:obj:`vikit_api_key <vikit_gateway.vikit_api_key>`
     - \-
   * - :py:obj:`vikit_backend_url <vikit_gateway.vikit_backend_url>`
     - \-


Classes
-------

.. py:class:: VikitGateway

   Bases: :py:obj:`vikit.gateways.ML_models_gateway.MLModelsGateway`

   A Gateway to interact with the Vikit API


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`compose_music_from_text_async <vikit_gateway.VikitGateway.compose_music_from_text_async>`\ (prompt_text, duration)
        - Compose a music for a prompt text
      * - :py:obj:`generate_background_music_async <vikit_gateway.VikitGateway.generate_background_music_async>`\ (duration, prompt)
        - Here we generate the music to add as background music
      * - :py:obj:`generate_mp3_from_text_async <vikit_gateway.VikitGateway.generate_mp3_from_text_async>`\ (prompt_text, target_file)
        - \-
      * - :py:obj:`generate_mp3_from_text_async_elevenlabs <vikit_gateway.VikitGateway.generate_mp3_from_text_async_elevenlabs>`\ (prompt_text, target_file)
        - Generate an mp3 file from a text prompt.
      * - :py:obj:`generate_seine_transition_async <vikit_gateway.VikitGateway.generate_seine_transition_async>`\ (source_image_path, target_image_path)
        - Generate a transition between two videos
      * - :py:obj:`generate_video_VideoCrafter2_async <vikit_gateway.VikitGateway.generate_video_VideoCrafter2_async>`\ (prompt)
        - Generate a video from the given prompt
      * - :py:obj:`generate_video_async <vikit_gateway.VikitGateway.generate_video_async>`\ (prompt, model_provider)
        - Generate a video from the given prompt
      * - :py:obj:`generate_video_from_image_stabilityai_async <vikit_gateway.VikitGateway.generate_video_from_image_stabilityai_async>`\ (prompt)
        - Generate a video from the given image prompt
      * - :py:obj:`generate_video_haiper_async <vikit_gateway.VikitGateway.generate_video_haiper_async>`\ (prompt)
        - Generate a video from the given prompt
      * - :py:obj:`generate_video_stabilityai_async <vikit_gateway.VikitGateway.generate_video_stabilityai_async>`\ (prompt)
        - Generate a video from the given prompt
      * - :py:obj:`get_enhanced_prompt_async <vikit_gateway.VikitGateway.get_enhanced_prompt_async>`\ (subtitleText)
        - Generates an enhanced prompt from an original one, probably written by a user or
      * - :py:obj:`get_keywords_from_prompt_async <vikit_gateway.VikitGateway.get_keywords_from_prompt_async>`\ (subtitleText, excluded_words)
        - Generates keywords from a subtitle text using the Replicate API.
      * - :py:obj:`get_music_generation_keywords_async <vikit_gateway.VikitGateway.get_music_generation_keywords_async>`\ (text)
        - Generate keywords from a text using the Replicate API
      * - :py:obj:`get_subtitles_async <vikit_gateway.VikitGateway.get_subtitles_async>`\ (audiofile_path)
        - Extract subtitles from an audio file using the Replicate API
      * - :py:obj:`interpolate_async <vikit_gateway.VikitGateway.interpolate_async>`\ (video)
        - Run some interpolation magic. This model may fail after timeout, so you


   .. rubric:: Members

   .. py:method:: compose_music_from_text_async(prompt_text: str, duration: int)
      :async:


      Compose a music for a prompt text

      :param prompt_text: The text prompt
      :param duration: The duration of the music

      :returns: The link to the generated music


   .. py:method:: generate_background_music_async(duration: int = 3, prompt: str = None) -> str
      :async:


      Here we generate the music to add as background music

      :param - duration: int - the duration of the music in seconds
      :param - prompt: str - the prompt to generate the music from

      :returns: the path to the generated music
      :rtype: - str


   .. py:method:: generate_mp3_from_text_async(prompt_text: str, target_file: str)
      :async:


   .. py:method:: generate_mp3_from_text_async_elevenlabs(prompt_text: str, target_file: str)
      :async:


      Generate an mp3 file from a text prompt.

      :param - prompt_text: str - the text to generate the mp3 from
      :param - target_file: str - the path to the target file

      :returns:

                - None


   .. py:method:: generate_seine_transition_async(source_image_path, target_image_path)
      :async:


      Generate a transition between two videos

      :param index: The index of the video
      :param initial: Whether this is the initial video

      :returns: The link to the generated video


   .. py:method:: generate_video_VideoCrafter2_async(prompt: str)
      :async:


      Generate a video from the given prompt

      :param prompt: The prompt to generate the video from

      :returns: The link to the generated video


   .. py:method:: generate_video_async(prompt: str, model_provider: str)
      :async:


      Generate a video from the given prompt

      :param prompt: The prompt to generate the video from
      :param model_provider: The model provider to use

      :returns: The path to the generated video


   .. py:method:: generate_video_from_image_stabilityai_async(prompt: str)
      :async:


      Generate a video from the given image prompt

      :param prompt: Image prompt to generate the video from in base64 format

      :returns: The link to the generated video


   .. py:method:: generate_video_haiper_async(prompt: str)
      :async:


      Generate a video from the given prompt

      :param prompt: The prompt to generate the video from

      :returns: The link to the generated video


   .. py:method:: generate_video_stabilityai_async(prompt: str)
      :async:


      Generate a video from the given prompt

      :param prompt: The prompt to generate the video from

      :returns: The link to the generated video


   .. py:method:: get_enhanced_prompt_async(subtitleText)
      :async:


      Generates an enhanced prompt from an original one, probably written by a user or
      translated from an audio

      :param A subtitle text:

      :returns: A prompt enhanced by an LLM


   .. py:method:: get_keywords_from_prompt_async(subtitleText, excluded_words: str = None)
      :async:


      Generates keywords from a subtitle text using the Replicate API.

      :param A subtitle text:

      :returns: A list of keywords generated by an LLM using the subtitle text


   .. py:method:: get_music_generation_keywords_async(text) -> str
      :async:


      Generate keywords from a text using the Replicate API

      At the end of the resulting prompt we get 3 words that will be used to generate a file name out of
      the generated keywords

      :param text: The text to generate keywords from

      :returns: A list of keywords


   .. py:method:: get_subtitles_async(audiofile_path)
      :async:


      Extract subtitles from an audio file using the Replicate API

      :param i: The index of the audio slice
      :type i: int

      :returns: The subtitles obtained from the Replicate API
      :rtype: subs


   .. py:method:: interpolate_async(video)
      :async:


      Run some interpolation magic. This model may fail after timeout, so you
      should call it with retry logic

      :param video: The video to interpolate

      :returns: a link to the interpolated video





Attributes
----------
.. py:data:: KEYWORDS_FORMAT_PROMPT
   :value: "' Just list the keywords in english language, separated by a coma, do not re-output the prompt....


.. py:data:: http_timeout

.. py:data:: vikit_api_key

.. py:data:: vikit_backend_url
   :value: 'https://videho.replit.app/models'




