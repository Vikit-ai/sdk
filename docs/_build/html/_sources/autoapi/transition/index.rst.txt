
transition
==========

.. py:module:: transition


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`Transition <transition.Transition>`
     - Base class for transitions between videos.




Classes
-------

.. py:class:: Transition(source_video: vikit.video.video.Video, target_video: vikit.video.video.Video)

   Bases: :py:obj:`vikit.video.video.Video`

   Base class for transitions between videos.


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`generate_background_music_prompt <transition.Transition.generate_background_music_prompt>`\ ()
        - Get the background music prompt from the source and target videos.
      * - :py:obj:`get_title <transition.Transition.get_title>`\ ()
        - \-


   .. rubric:: Members

   .. py:method:: generate_background_music_prompt()

      Get the background music prompt from the source and target videos.

      :returns: The background music prompt
      :rtype: str


   .. py:method:: get_title()






