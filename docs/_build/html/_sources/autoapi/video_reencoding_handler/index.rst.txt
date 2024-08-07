
video_reencoding_handler
========================

.. py:module:: video_reencoding_handler


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`VideoReencodingHandler <video_reencoding_handler.VideoReencodingHandler>`
     - \-




Classes
-------

.. py:class:: VideoReencodingHandler

   Bases: :py:obj:`vikit.common.handler.Handler`


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`execute_async <video_reencoding_handler.VideoReencodingHandler.execute_async>`\ (video)
        - Process the video to reencode and normalize binaries, i.e. make it so the


   .. rubric:: Members

   .. py:method:: execute_async(video)
      :async:


      Process the video to reencode and normalize binaries, i.e. make it so the
      different video composing a composite have the same format

      :param args: The arguments: video, build_settings

      :returns: The composite video
      :rtype: CompositeVideo







