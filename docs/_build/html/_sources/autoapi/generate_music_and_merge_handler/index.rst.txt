
generate_music_and_merge_handler
================================

.. py:module:: generate_music_and_merge_handler


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`GenerateMusicAndMergeHandler <generate_music_and_merge_handler.GenerateMusicAndMergeHandler>`
     - \-




Classes
-------

.. py:class:: GenerateMusicAndMergeHandler(music_duration: float, bg_music_prompt: str = None)

   Bases: :py:obj:`vikit.common.handler.Handler`


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`execute_async <generate_music_and_merge_handler.GenerateMusicAndMergeHandler.execute_async>`\ (video)
        - Generate a background music based on the prompt and merge it with the video


   .. rubric:: Members

   .. py:method:: execute_async(video)
      :async:


      Generate a background music based on the prompt and merge it with the video

      :param video: The video to process
      :type video: Video

      :returns: The composite video
      :rtype: CompositeVideo







