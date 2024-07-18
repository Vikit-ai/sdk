prompt_based_video
==================

.. py:module:: prompt_based_video


Classes
-------

.. autoapisummary::

   prompt_based_video.PromptBasedVideo


Module Contents
---------------


.. py:class:: PromptBasedVideo(prompt=None)

   Bases: :py:obj:`vikit.video.video.Video`

   PromptBasedVideo is a simple way to generate a video based out of a text prompt

   It creates a master composite video which embeds as many composite video as there are subtitles
   in the given prompt.

   We do some form of inheritance by composition to prevent circular dependencies and benefit from more modularity


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`build <prompt_based_video.PromptBasedVideo.build>`\ (build_settings)
        - Generate the actual inner video
      * - :py:obj:`get_file_name_by_state <prompt_based_video.PromptBasedVideo.get_file_name_by_state>`\ (build_settings)
        - Get the file name of the video
      * - :py:obj:`get_title <prompt_based_video.PromptBasedVideo.get_title>`\ ()
        - Title of the prompt based video, generated from an LLM. If not available, we generate it from the prompt


   .. rubric:: Members

   .. py:method:: build(build_settings=VideoBuildSettings())

      Generate the actual inner video

      Params:
          - build_settings: allow some customization

      Returns:
          The current instance


   .. py:method:: get_file_name_by_state(build_settings: vikit.video.video.VideoBuildSettings)

      Get the file name of the video

      Returns:
          str: The file name of the video


   .. py:method:: get_title()

      Title of the prompt based video, generated from an LLM. If not available, we generate it from the prompt



