
prompt_factory
==============

.. py:module:: prompt_factory


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`PromptFactory <prompt_factory.PromptFactory>`
     - Prompt factory helps getting the right sub class of Prompt depending on




Classes
-------

.. py:class:: PromptFactory(ml_gateway: vikit.gateways.ML_models_gateway.MLModelsGateway = None, prompt_build_settings: vikit.prompt.prompt_build_settings.PromptBuildSettings = None)

   Prompt factory helps getting the right sub class of Prompt depending on
   the input provided. We use the right builder class to make it clear of the operations
   required to build each type of prompt and optimise it

   This is also useful to simplify unit testing of prompts as we will inject custom made Prompt objects
   instead of letting builders run some complex stuff involving external services


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`create_prompt_from_audio_file <prompt_factory.PromptFactory.create_prompt_from_audio_file>`\ (recorded_audio_prompt_path)
        - Create a prompt object from a recorded audio file
      * - :py:obj:`create_prompt_from_audio_file_async <prompt_factory.PromptFactory.create_prompt_from_audio_file_async>`\ (recorded_audio_prompt_path)
        - Create a prompt object from a recorded audio file
      * - :py:obj:`create_prompt_from_image <prompt_factory.PromptFactory.create_prompt_from_image>`\ (image_path, text)
        - Create a prompt object from a prompt image path
      * - :py:obj:`create_prompt_from_text <prompt_factory.PromptFactory.create_prompt_from_text>`\ (prompt_text)
        - Create a recorded prompt object from a text by  creating
      * - :py:obj:`get_prompt_handler_chain <prompt_factory.PromptFactory.get_prompt_handler_chain>`\ (prompt_build_settings)
        - Get the handler chain of the Prompt. Can includes handlers to prepare
      * - :py:obj:`get_reengineered_prompt_text_from_raw_text <prompt_factory.PromptFactory.get_reengineered_prompt_text_from_raw_text>`\ (prompt, prompt_build_settings)
        - Get a reengineered prompt from a raw text , using build settings


   .. rubric:: Members

   .. py:method:: create_prompt_from_audio_file(recorded_audio_prompt_path: str = None)
      :async:


      Create a prompt object from a recorded audio file

      :param - recorded_audio_prompt_path: the path to the recorded audio file

      :returns: self


   .. py:method:: create_prompt_from_audio_file_async(recorded_audio_prompt_path: str = None)
      :async:


      Create a prompt object from a recorded audio file

      :param - recorded_audio_prompt_path: the path to the recorded audio file

      :returns: self


   .. py:method:: create_prompt_from_image(image_path: str = None, text: str = None)

      Create a prompt object from a prompt image path

      :param - prompt_image: the image of the prompt

      :returns: self


   .. py:method:: create_prompt_from_text(prompt_text: str = None)
      :async:


      Create a recorded prompt object from a text by  creating
      a recorded audio file using a ML Model, then extracting the subtitles,
      i.e. all the sentences text and timings

      :param - prompt_text: the text of the prompt

      :returns: a RecordedPrompt object


   .. py:method:: get_prompt_handler_chain(prompt_build_settings: vikit.prompt.prompt_build_settings.PromptBuildSettings) -> list[vikit.common.handler.Handler]

      Get the handler chain of the Prompt. Can includes handlers to prepare
      the prompt text by adding more verbosity, or to filter ofensing words, limit
      the prompt length, etc

      :param build_settings: The settings to use for building the prompt
      :type build_settings: PromptBuildSettings

      :returns: The list of handlers to use for building the video
      :rtype: list


   .. py:method:: get_reengineered_prompt_text_from_raw_text(prompt: str, prompt_build_settings: vikit.prompt.prompt_build_settings.PromptBuildSettings) -> str
      :async:


      Get a reengineered prompt from a raw text , using build settings
      to guide how we should build the prompt

      :param prompt: The text prompt
      :type prompt: str

      :returns: The prompt object
      :rtype: Prompt







