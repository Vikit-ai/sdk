
text_prompt_builder
===================

.. py:module:: text_prompt_builder


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`TextPromptBuilder <text_prompt_builder.TextPromptBuilder>`
     - Builds a text prompt




Classes
-------

.. py:class:: TextPromptBuilder

   Builds a text prompt

   Most functions are used by a prompt builder, as the way to generate a prompt may vary and get a bit complex


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`build <text_prompt_builder.TextPromptBuilder.build>`\ ()
        - \-
      * - :py:obj:`set_prompt_text <text_prompt_builder.TextPromptBuilder.set_prompt_text>`\ (text)
        - \-
      * - :py:obj:`set_recording <text_prompt_builder.TextPromptBuilder.set_recording>`\ (recording_path)
        - set the recording path
      * - :py:obj:`set_subtitles <text_prompt_builder.TextPromptBuilder.set_subtitles>`\ (subs)
        - set the prompt text using an LLM which extracts it from the recorded file


   .. rubric:: Members

   .. py:method:: build()

   .. py:method:: set_prompt_text(text: str)

   .. py:method:: set_recording(recording_path: str)

      set the recording path


   .. py:method:: set_subtitles(subs: list[pysrt.SubRipItem])

      set the prompt text using an LLM which extracts it from the recorded file







