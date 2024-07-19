
recorded_prompt_builder
=======================

.. py:module:: recorded_prompt_builder


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`RecordedPromptBuilder <recorded_prompt_builder.RecordedPromptBuilder>`
     - Builds a prompt based on a recorded audio file




Classes
-------

.. py:class:: RecordedPromptBuilder

   Builds a prompt based on a recorded audio file

   Most functions are used by a prompt builder, as the way to generate a prompt may vary and get a bit complex



   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`build <recorded_prompt_builder.RecordedPromptBuilder.build>`\ ()
        - \-
      * - :py:obj:`convert_recorded_audio_prompt_path <recorded_prompt_builder.RecordedPromptBuilder.convert_recorded_audio_prompt_path>`\ (recorded_audio_prompt_path, prompt_mp3_file_name)
        - Convert the recorded audio prompt to mp3
      * - :py:obj:`set_subtitles <recorded_prompt_builder.RecordedPromptBuilder.set_subtitles>`\ (subs)
        - set the prompt text using an LLM which extracts it from the recorded file
      * - :py:obj:`set_text <recorded_prompt_builder.RecordedPromptBuilder.set_text>`\ (text)
        - Set the text prompt


   .. rubric:: Members

   .. py:method:: build()

   .. py:method:: convert_recorded_audio_prompt_path(recorded_audio_prompt_path: str, prompt_mp3_file_name=None)

      Convert the recorded audio prompt to mp3

      :param recorded_audio_prompt_path: The path to the recorded audio file
      :param prompt_mp3_file_name: The name of the mp3 file to save the recording as


   .. py:method:: set_subtitles(subs: list[pysrt.SubRipItem])

      set the prompt text using an LLM which extracts it from the recorded file


   .. py:method:: set_text(text: str)

      Set the text prompt

      :param text: The text prompt







