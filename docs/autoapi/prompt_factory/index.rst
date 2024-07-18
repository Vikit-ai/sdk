prompt_factory
==============

.. py:module:: prompt_factory


Classes
-------

.. autoapisummary::

   prompt_factory.PromptFactory


Module Contents
---------------


.. py:class:: PromptFactory(ml_gateway: vikit.gateways.ML_models_gateway.MLModelsGateway = None)

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
      * - :py:obj:`create_prompt_from_text <prompt_factory.PromptFactory.create_prompt_from_text>`\ (prompt_text, generate_recording)
        - Create a prompt object from a prompt text by possibly creating


   .. rubric:: Members

   .. py:method:: create_prompt_from_audio_file(recorded_audio_prompt_path: str = None)

      Create a prompt object from a recorded audio file

      args:
          - recorded_audio_prompt_path: the path to the recorded audio file

      returns:
          self



   .. py:method:: create_prompt_from_text(prompt_text: str = None, generate_recording: bool = True)

      Create a prompt object from a prompt text by possibly creating
      a recorded  audio file using a ML Model if asked to do so

      args:
          - prompt_text: the text of the prompt
          - generate_recording: a boolean to indicate if we should generate a recording from the text
          before extracting subtitles

      returns:
          self



