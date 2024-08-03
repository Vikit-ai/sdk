
ML_models_gateway
=================

.. py:module:: ML_models_gateway


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`MLModelsGateway <ML_models_gateway.MLModelsGateway>`
     - This class is a gateway to a remote API hosting Machine Learning models as a service.




Classes
-------

.. py:class:: MLModelsGateway

   Bases: :py:obj:`abc.ABC`

   This class is a gateway to a remote API hosting Machine Learning models as a service.
   It abstracts the main features needed to interact with the API

   Stubs inheriting from this class may be created for each model to be used so as to prevent
   dependencies on the actual API implementation and speed up tests


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`cleanse_llm_keywords_async <ML_models_gateway.MLModelsGateway.cleanse_llm_keywords_async>`\ ()
        - \-
      * - :py:obj:`compose_music_from_text_async <ML_models_gateway.MLModelsGateway.compose_music_from_text_async>`\ (prompt_text, duration)
        - :summarylabel:`abc` \-
      * - :py:obj:`generate_background_music_async <ML_models_gateway.MLModelsGateway.generate_background_music_async>`\ (duration, prompt, target_file_name)
        - :summarylabel:`abc` \-
      * - :py:obj:`generate_mp3_from_text_async <ML_models_gateway.MLModelsGateway.generate_mp3_from_text_async>`\ (prompt_text, target_file)
        - \-
      * - :py:obj:`generate_seine_transition_async <ML_models_gateway.MLModelsGateway.generate_seine_transition_async>`\ (source_image_path, target_image_path)
        - :summarylabel:`abc` \-
      * - :py:obj:`generate_video_async <ML_models_gateway.MLModelsGateway.generate_video_async>`\ (prompt, model_provider)
        - :summarylabel:`abc` \-
      * - :py:obj:`get_enhanced_prompt_async <ML_models_gateway.MLModelsGateway.get_enhanced_prompt_async>`\ (subtitleText)
        - :summarylabel:`abc` \-
      * - :py:obj:`get_keywords_from_prompt_async <ML_models_gateway.MLModelsGateway.get_keywords_from_prompt_async>`\ (subtitleText, excluded_words)
        - :summarylabel:`abc` \-
      * - :py:obj:`get_music_generation_keywords_async <ML_models_gateway.MLModelsGateway.get_music_generation_keywords_async>`\ (text)
        - :summarylabel:`abc` \-
      * - :py:obj:`get_subtitles_async <ML_models_gateway.MLModelsGateway.get_subtitles_async>`\ (audiofile_path)
        - :summarylabel:`abc` \-
      * - :py:obj:`interpolate_async <ML_models_gateway.MLModelsGateway.interpolate_async>`\ (video)
        - :summarylabel:`abc` \-


   .. rubric:: Members

   .. py:method:: cleanse_llm_keywords_async()

   .. py:method:: compose_music_from_text_async(prompt_text: str, duration: int)
      :abstractmethod:

      :async:


   .. py:method:: generate_background_music_async(duration: int = 3, prompt: str = None, target_file_name: str = None) -> str
      :abstractmethod:

      :async:


   .. py:method:: generate_mp3_from_text_async(prompt_text, target_file)
      :async:


   .. py:method:: generate_seine_transition_async(source_image_path, target_image_path)
      :abstractmethod:

      :async:


   .. py:method:: generate_video_async(prompt: str, model_provider: str)
      :abstractmethod:


   .. py:method:: get_enhanced_prompt_async(subtitleText)
      :abstractmethod:

      :async:


   .. py:method:: get_keywords_from_prompt_async(subtitleText, excluded_words: str = None)
      :abstractmethod:

      :async:


   .. py:method:: get_music_generation_keywords_async(text) -> str
      :abstractmethod:

      :async:


   .. py:method:: get_subtitles_async(audiofile_path: str)
      :abstractmethod:

      :async:


   .. py:method:: interpolate_async(video)
      :abstractmethod:

      :async:







