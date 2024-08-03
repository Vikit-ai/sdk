
gen_read_aloud_prompt_and_audio_merging_handler
===============================================

.. py:module:: gen_read_aloud_prompt_and_audio_merging_handler


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`ReadAloudPromptAudioMergingHandler <gen_read_aloud_prompt_and_audio_merging_handler.ReadAloudPromptAudioMergingHandler>`
     - Handler used to apply a synthetic voice to the video, as an audio prompt




Classes
-------

.. py:class:: ReadAloudPromptAudioMergingHandler(recorded_prompt)

   Bases: :py:obj:`vikit.common.handler.Handler`

   Handler used to apply a synthetic voice to the video, as an audio prompt


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`execute_async <gen_read_aloud_prompt_and_audio_merging_handler.ReadAloudPromptAudioMergingHandler.execute_async>`\ (video)
        - Merge prompt generated recording with video  as a single media file


   .. rubric:: Members

   .. py:method:: execute_async(video)
      :async:


      Merge prompt generated recording with video  as a single media file

      :param video: The video to process
      :type video: Video

      :returns: The video including generated synthetic voice that reads the prompt







