ML_models_gateway
=================

.. py:module:: ML_models_gateway


Classes
-------

.. autoapisummary::

   ML_models_gateway.MLModelsGateway


Module Contents
---------------


.. py:class:: MLModelsGateway

   Bases: :py:obj:`pydantic.BaseModel`, :py:obj:`abc.ABC`

   This class is a gateway to a remote API hosting Machine Learning models as a service.
   It abstracts the main features needed to interact with the API

   Stubs inheriting from this class may be created for each model to be used so as to prevent
   dependencies on the actual API implementation and speed up tests


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`generate_background_music <ML_models_gateway.MLModelsGateway.generate_background_music>`\ (duration, prompt)
        - \-
      * - :py:obj:`generate_seine_transition <ML_models_gateway.MLModelsGateway.generate_seine_transition>`\ (source_image_path, target_image_path)
        - \-
      * - :py:obj:`cleanse_llm_keywords <ML_models_gateway.MLModelsGateway.cleanse_llm_keywords>`\ ()
        - \-
      * - :py:obj:`compose_music_from_text <ML_models_gateway.MLModelsGateway.compose_music_from_text>`\ (prompt_text, duration)
        - \-
      * - :py:obj:`get_music_generation_keywords <ML_models_gateway.MLModelsGateway.get_music_generation_keywords>`\ (text)
        - \-
      * - :py:obj:`interpolate <ML_models_gateway.MLModelsGateway.interpolate>`\ (video)
        - \-
      * - :py:obj:`get_keywords_from_prompt <ML_models_gateway.MLModelsGateway.get_keywords_from_prompt>`\ (subtitleText, excluded_words)
        - \-
      * - :py:obj:`get_enhanced_prompt <ML_models_gateway.MLModelsGateway.get_enhanced_prompt>`\ (subtitleText)
        - \-
      * - :py:obj:`get_subtitles <ML_models_gateway.MLModelsGateway.get_subtitles>`\ (audiofile_path)
        - \-
      * - :py:obj:`generate_video <ML_models_gateway.MLModelsGateway.generate_video>`\ (prompt)
        - :summarylabel:`abc` \-


   .. rubric:: Members

   .. py:method:: generate_background_music(duration: int = 3, prompt: str = None) -> str

   .. py:method:: generate_seine_transition(source_image_path, target_image_path)

   .. py:method:: cleanse_llm_keywords()

   .. py:method:: compose_music_from_text(prompt_text: str, duration: int)

   .. py:method:: get_music_generation_keywords(text) -> str

   .. py:method:: interpolate(video)

   .. py:method:: get_keywords_from_prompt(subtitleText, excluded_words: str = None)

   .. py:method:: get_enhanced_prompt(subtitleText)

   .. py:method:: get_subtitles(audiofile_path: str)

   .. py:method:: generate_video(prompt: str)
      :abstractmethod:



