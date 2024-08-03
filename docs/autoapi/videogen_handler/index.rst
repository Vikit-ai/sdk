
videogen_handler
================

.. py:module:: videogen_handler


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`VideoGenHandler <videogen_handler.VideoGenHandler>`
     - \-




Classes
-------

.. py:class:: VideoGenHandler(video_gen_text_prompt: str = None)

   Bases: :py:obj:`vikit.common.handler.Handler`


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`execute_async <videogen_handler.VideoGenHandler.execute_async>`\ (video)
        - Process the video generation binaries: the video binary is generated from Gen AI, hosted behind an API


   .. rubric:: Members

   .. py:method:: execute_async(video: vikit.video.video.Video)
      :async:


      Process the video generation binaries: the video binary is generated from Gen AI, hosted behind an API
      which could be distant as well as local. The video binary is then stored in a web storage or locally.

      :param video: The video to process
      :type video: Video

      :returns: The video with the media URL set to the generated video







