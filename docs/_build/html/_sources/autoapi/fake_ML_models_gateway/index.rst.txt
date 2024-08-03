
fake_ML_models_gateway
======================

.. py:module:: fake_ML_models_gateway


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`FakeMLModelsGateway <fake_ML_models_gateway.FakeMLModelsGateway>`
     - This class is a gateway to a remote API hosting Machine Learning models as a service.



.. list-table:: Attributes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`STUDENT_ARM_WRITING <fake_ML_models_gateway.STUDENT_ARM_WRITING>`
     - \-
   * - :py:obj:`TESTS_MEDIA_FOLDER <fake_ML_models_gateway.TESTS_MEDIA_FOLDER>`
     - \-


Classes
-------

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

      * - :py:obj:`cleanse_llm_keywords <fake_ML_models_gateway.FakeMLModelsGateway.cleanse_llm_keywords>`\ (input)
        - \-
      * - :py:obj:`compose_music_from_text_async <fake_ML_models_gateway.FakeMLModelsGateway.compose_music_from_text_async>`\ (prompt_text, duration, sleep_time)
        - \-
      * - :py:obj:`extract_audio_slice <fake_ML_models_gateway.FakeMLModelsGateway.extract_audio_slice>`\ (i, end, audiofile_path, target_file_name)
        - \-
      * - :py:obj:`extract_audio_slice_async <fake_ML_models_gateway.FakeMLModelsGateway.extract_audio_slice_async>`\ (i, end, audiofile_path, target_file_name, sleep_time)
        - \-
      * - :py:obj:`generate_background_music_async <fake_ML_models_gateway.FakeMLModelsGateway.generate_background_music_async>`\ (duration, prompt, sleep_time)
        - \-
      * - :py:obj:`generate_mp3_from_text_async <fake_ML_models_gateway.FakeMLModelsGateway.generate_mp3_from_text_async>`\ (prompt_text, target_file)
        - \-
      * - :py:obj:`generate_seine_transition_async <fake_ML_models_gateway.FakeMLModelsGateway.generate_seine_transition_async>`\ (source_image_path, target_image_path, sleep_time)
        - \-
      * - :py:obj:`generate_video_async <fake_ML_models_gateway.FakeMLModelsGateway.generate_video_async>`\ (prompt, sleep_time, model_provider)
        - \-
      * - :py:obj:`get_enhanced_prompt_async <fake_ML_models_gateway.FakeMLModelsGateway.get_enhanced_prompt_async>`\ (subtitleText, excluded_words, sleep_time)
        - \-
      * - :py:obj:`get_keywords_from_prompt <fake_ML_models_gateway.FakeMLModelsGateway.get_keywords_from_prompt>`\ (subtitleText, excluded_words, sleep_time)
        - \-
      * - :py:obj:`get_keywords_from_prompt_async <fake_ML_models_gateway.FakeMLModelsGateway.get_keywords_from_prompt_async>`\ (subtitleText, excluded_words, sleep_time)
        - \-
      * - :py:obj:`get_music_generation_keywords_async <fake_ML_models_gateway.FakeMLModelsGateway.get_music_generation_keywords_async>`\ (text, sleep_time)
        - \-
      * - :py:obj:`get_subtitles <fake_ML_models_gateway.FakeMLModelsGateway.get_subtitles>`\ (audiofile_path, sleep_time)
        - \-
      * - :py:obj:`get_subtitles_async <fake_ML_models_gateway.FakeMLModelsGateway.get_subtitles_async>`\ (audiofile_path, sleep_time)
        - \-
      * - :py:obj:`interpolate_async <fake_ML_models_gateway.FakeMLModelsGateway.interpolate_async>`\ (link_to_video, sleep_time)
        - \-
      * - :py:obj:`sleep <fake_ML_models_gateway.FakeMLModelsGateway.sleep>`\ (sleep_time)
        - \-


   .. rubric:: Members

   .. py:method:: cleanse_llm_keywords(input)

   .. py:method:: compose_music_from_text_async(prompt_text: str, duration: int, sleep_time: int = 0)
      :async:


   .. py:method:: extract_audio_slice(i, end, audiofile_path, target_file_name: str = None)

   .. py:method:: extract_audio_slice_async(i, end, audiofile_path, target_file_name: str = None, sleep_time: int = 0)
      :async:


   .. py:method:: generate_background_music_async(duration: float = 3, prompt: str = None, sleep_time: int = 0) -> str
      :async:


   .. py:method:: generate_mp3_from_text_async(prompt_text, target_file: str = None)
      :async:


   .. py:method:: generate_seine_transition_async(source_image_path, target_image_path, sleep_time: int = 0)
      :async:


   .. py:method:: generate_video_async(prompt: str = None, sleep_time: int = 0, model_provider: str = None)
      :async:


   .. py:method:: get_enhanced_prompt_async(subtitleText, excluded_words: str = None, sleep_time: int = 0)
      :async:


   .. py:method:: get_keywords_from_prompt(subtitleText, excluded_words: str = None, sleep_time: int = 0)
      :async:


   .. py:method:: get_keywords_from_prompt_async(subtitleText, excluded_words: str = None, sleep_time: int = 0)
      :async:


   .. py:method:: get_music_generation_keywords_async(text, sleep_time: int = 0) -> str
      :async:


   .. py:method:: get_subtitles(audiofile_path, sleep_time: int = 0)
      :async:


   .. py:method:: get_subtitles_async(audiofile_path, sleep_time: int = 0)
      :async:


   .. py:method:: interpolate_async(link_to_video: str, sleep_time: int = 0)
      :async:


   .. py:method:: sleep(sleep_time=1)




Attributes
----------
.. py:data:: STUDENT_ARM_WRITING
   :value: 'student_arm_writting.mp4'


.. py:data:: TESTS_MEDIA_FOLDER
   :value: 'tests/medias/'




