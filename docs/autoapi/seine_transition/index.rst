
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

      * - :py:obj:`build <seine_transition.SeineTransition.build>`\ (build_settings)
        - Apply the Seine transition between the source and target video


   .. rubric:: Members

   .. py:method:: build(build_settings: vikit.video.video.VideoBuildSettings = None) -> vikit.video.transition.Transition

      Apply the Seine transition between the source and target video

      :param build_settings: The settings for building the video
      :type build_settings: VideoBuildSettings

      :returns: The path to the generated transition video
      :rtype: str







