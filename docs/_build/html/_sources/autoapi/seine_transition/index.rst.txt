
seine_transition
================

.. py:module:: seine_transition


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`SeineTransition <seine_transition.SeineTransition>`
     - \-




Classes
-------

.. py:class:: SeineTransition(source_video: vikit.video.video.Video, target_video: vikit.video.video.Video)

   Bases: :py:obj:`vikit.video.transition.Transition`


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`get_core_handlers <seine_transition.SeineTransition.get_core_handlers>`\ (build_settings)
        - Get the handler chain of the video.


   .. rubric:: Members

   .. py:method:: get_core_handlers(build_settings: vikit.video.video.VideoBuildSettings) -> list[vikit.common.handler.Handler]

      Get the handler chain of the video.
      Defining the handler chain is the main way to define how the video is built
      so it is up to the child classes to implement this method

      At this stage, we should already have the enhanced prompt and title for this video

      :returns: The list of handlers to use for building the video
      :rtype: list







