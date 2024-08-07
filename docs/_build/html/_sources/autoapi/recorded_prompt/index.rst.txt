
recorded_prompt
===============

.. py:module:: recorded_prompt


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`RecordedPrompt <recorded_prompt.RecordedPrompt>`
     - A class to represent a prompt generated from a recorded audio file. You may want to use this class




Classes
-------

.. py:class:: RecordedPrompt(audio_recording=None, subtitles=None, duration=None, text=None)

   Bases: :py:obj:`vikit.prompt.prompt.Prompt`

   A class to represent a prompt generated from a recorded audio file. You may want to use this class
   to generate a prompt from a recorded audio file, like a podcast or a video soundtrack (e.g. a musical video clip)


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`convert_recorded_audio_prompt_path_to_mp3 <recorded_prompt.RecordedPrompt.convert_recorded_audio_prompt_path_to_mp3>`\ (recorded_audio_prompt_path, prompt_mp3_file_name)
        - Convert the recorded audio prompt to mp3
      * - :py:obj:`get_full_text <recorded_prompt.RecordedPrompt.get_full_text>`\ ()
        - Returns the full text of the prompt


   .. rubric:: Members

   .. py:method:: convert_recorded_audio_prompt_path_to_mp3(recorded_audio_prompt_path: str, prompt_mp3_file_name=None)
      :async:


      Convert the recorded audio prompt to mp3

      :param recorded_audio_prompt_path: The path to the recorded audio file
      :param prompt_mp3_file_name: The name of the mp3 file to save the recording as


   .. py:method:: get_full_text() -> str

      Returns the full text of the prompt







