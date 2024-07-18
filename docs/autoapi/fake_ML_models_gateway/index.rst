fake_ML_models_gateway
======================

.. py:module:: fake_ML_models_gateway


Attributes
----------

.. autoapisummary::

   fake_ML_models_gateway.TESTS_MEDIA_FOLDER
   fake_ML_models_gateway.STUDENT_ARM_WRITING


Classes
-------

.. autoapisummary::

   fake_ML_models_gateway.FakeMLModelsGateway


Module Contents
---------------

.. py:data:: TESTS_MEDIA_FOLDER
   :value: 'tests/medias/'


.. py:data:: STUDENT_ARM_WRITING
   :value: 'student_arm_writting.mp4'



.. py:class:: FakeMLModelsGateway

   Bases: :py:obj:`vikit.gateways.ML_models_gateway.MLModelsGateway`

   This class is a gateway to a remote API hosting Machine Learning models as a service.
   It abstracts the main features needed to interact with the API

   Stubs inheriting from this class may be created for each model to be used so as to prevent
   dependencies on the actual API implementation and speed up tests


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`generate_background_music <fake_ML_models_gateway.FakeMLModelsGateway.generate_background_music>`\ (duration, prompt)
        - \-
      * - :py:obj:`generate_seine_transition <fake_ML_models_gateway.FakeMLModelsGateway.generate_seine_transition>`\ (source_image_path, target_image_path)
        - \-
      * - :py:obj:`cleanse_llm_keywords <fake_ML_models_gateway.FakeMLModelsGateway.cleanse_llm_keywords>`\ (input)
        - \-
      * - :py:obj:`compose_music_from_text <fake_ML_models_gateway.FakeMLModelsGateway.compose_music_from_text>`\ (prompt_text, duration)
        - \-
      * - :py:obj:`get_music_generation_keywords <fake_ML_models_gateway.FakeMLModelsGateway.get_music_generation_keywords>`\ (text)
        - \-
      * - :py:obj:`interpolate <fake_ML_models_gateway.FakeMLModelsGateway.interpolate>`\ (link_to_video)
        - \-
      * - :py:obj:`get_keywords_from_prompt <fake_ML_models_gateway.FakeMLModelsGateway.get_keywords_from_prompt>`\ (subtitleText, excluded_words)
        - \-
      * - :py:obj:`get_enhanced_prompt <fake_ML_models_gateway.FakeMLModelsGateway.get_enhanced_prompt>`\ (subtitleText)
        - \-
      * - :py:obj:`get_subtitles <fake_ML_models_gateway.FakeMLModelsGateway.get_subtitles>`\ (audiofile_path)
        - \-
      * - :py:obj:`generate_video <fake_ML_models_gateway.FakeMLModelsGateway.generate_video>`\ (prompt)
        - \-
      * - :py:obj:`extract_audio_slice <fake_ML_models_gateway.FakeMLModelsGateway.extract_audio_slice>`\ (i, end, audiofile_path, target_file_name)
        - \-


   .. rubric:: Members

   .. py:method:: generate_background_music(duration: float = 3, prompt: str = None) -> str

   .. py:method:: generate_seine_transition(source_image_path, target_image_path)

   .. py:method:: cleanse_llm_keywords(input)

   .. py:method:: compose_music_from_text(prompt_text: str, duration: int)

   .. py:method:: get_music_generation_keywords(text) -> str

   .. py:method:: interpolate(link_to_video: str)

   .. py:method:: get_keywords_from_prompt(subtitleText, excluded_words: str = None)

   .. py:method:: get_enhanced_prompt(subtitleText)

   .. py:method:: get_subtitles(audiofile_path)

   .. py:method:: generate_video(prompt: str = None)

   .. py:method:: extract_audio_slice(i, end, audiofile_path, target_file_name: str = None)


