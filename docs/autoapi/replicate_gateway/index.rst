
replicate_gateway
=================

.. py:module:: replicate_gateway


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`ReplicateGateway <replicate_gateway.ReplicateGateway>`
     - A class to represent the Replicate Gateway, a gateway to the Replicate API



.. list-table:: Attributes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`KEYWORDS_FORMAT_PROMPT <replicate_gateway.KEYWORDS_FORMAT_PROMPT>`
     - \-


Classes
-------

.. py:class:: ReplicateGateway

   Bases: :py:obj:`vikit.gateways.ML_models_gateway.MLModelsGateway`

   A class to represent the Replicate Gateway, a gateway to the Replicate API

   Replicate is a platform that allows to run AI models in the cloud


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`compose_music_from_text_async <replicate_gateway.ReplicateGateway.compose_music_from_text_async>`\ (prompt_text, duration)
        - Compose a music for a prompt text
      * - :py:obj:`generate_background_music_async <replicate_gateway.ReplicateGateway.generate_background_music_async>`\ (duration, prompt, target_file_name)
        - Here we generate the music to add as background music
      * - :py:obj:`generate_seine_transition_async <replicate_gateway.ReplicateGateway.generate_seine_transition_async>`\ (source_image_path, target_image_path)
        - Generate a transition between two videos
      * - :py:obj:`generate_video_async <replicate_gateway.ReplicateGateway.generate_video_async>`\ (prompt)
        - Generate a video from the given prompt
      * - :py:obj:`get_enhanced_prompt_async <replicate_gateway.ReplicateGateway.get_enhanced_prompt_async>`\ (subtitleText)
        - Generates an enhanced prompt from an original one, probably written by a user or
      * - :py:obj:`get_keywords_from_prompt_async <replicate_gateway.ReplicateGateway.get_keywords_from_prompt_async>`\ (subtitleText, excluded_words)
        - Generates keywords from a subtitle text using the Replicate API.
      * - :py:obj:`get_music_generation_keywords_async <replicate_gateway.ReplicateGateway.get_music_generation_keywords_async>`\ (text)
        - Generate keywords from a text using the Replicate API
      * - :py:obj:`get_subtitles_async <replicate_gateway.ReplicateGateway.get_subtitles_async>`\ (audiofile_path)
        - Extract subtitles from an audio file using the Replicate API
      * - :py:obj:`interpolate_async <replicate_gateway.ReplicateGateway.interpolate_async>`\ (video)
        - Run some interpolation magic. This model may fail after timeout, so you


   .. rubric:: Members

   .. py:method:: compose_music_from_text_async(prompt_text: str, duration: int)
      :async:


      Compose a music for a prompt text

      :param prompt_text: The text prompt
      :param duration: The duration of the music

      :returns: The link to the generated music


   .. py:method:: generate_background_music_async(duration: int = 3, prompt: str = None, target_file_name: str = None) -> str
      :async:


      Here we generate the music to add as background music

      :param duration: int - the duration of the music in seconds
      :param prompt: str - the prompt to generate the music from
      :param target_file_name: str - the name of the file to save the music to

      :returns: the path to the generated music
      :rtype: str


   .. py:method:: generate_seine_transition_async(source_image_path, target_image_path)
      :async:


      Generate a transition between two videos

      :param index: The index of the video
      :param initial: Whether this is the initial video

      :returns: The link to the generated video


   .. py:method:: generate_video_async(prompt: str)
      :async:


      Generate a video from the given prompt

      :param prompt: The prompt to generate the video from

      :returns: the video


   .. py:method:: get_enhanced_prompt_async(subtitleText)
      :async:


      Generates an enhanced prompt from an original one, probably written by a user or
      translated from an audio

      :param subtitleText: The original prompt

      :returns: A white space separated string of keywords composing the enhanced prompt


   .. py:method:: get_keywords_from_prompt_async(subtitleText, excluded_words: str = None)
      :async:


      Generates keywords from a subtitle text using the Replicate API.

      :param A subtitle text:

      :returns: A white space separated string of keywords


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
   :value: Multiline-String

   .. raw:: html

      <details><summary>Show Value</summary>

   .. code-block:: python

      """' Just list the keywords in english language, separated by a coma, do not re-output the prompt. 
                  The answer should be a list of keywords and exactly match the following format:  'KEYWORD1, KEYWORD2, KEYWORD3, etc' 
                  where KEYWORD1 and the other ones are generated by you. 
                  The last word of your answer should be a summary of all the other keywords so I can generate a file name 
                  out of it, it should be limited to three words joined by the underscore character and you should only use 
                  characters compatible with filenames in the summary, so only standard alphanumerical characters. Don't prefix the
                  summary with any special characters, just the words joined by underscores.'"""

   .. raw:: html

      </details>





