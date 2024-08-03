
prompt_based_video
==================

.. py:module:: prompt_based_video


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`PromptBasedVideo <prompt_based_video.PromptBasedVideo>`
     - PromptBasedVideo is a simple way to generate a video based out of a text prompt




Classes
-------

.. py:class:: PromptBasedVideo(prompt: vikit.prompt.prompt.Prompt = None)

   Bases: :py:obj:`vikit.video.composite_video.CompositeVideo`

   PromptBasedVideo is a simple way to generate a video based out of a text prompt

   It creates a master composite video which embeds as many composite video as there are subtitles
   in the given prompt.

   We do some form of inheritance by composition to prevent circular dependencies and benefit from more modularity


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`compose <prompt_based_video.PromptBasedVideo.compose>`\ (build_settings)
        - Compose the inner composite video
      * - :py:obj:`get_title <prompt_based_video.PromptBasedVideo.get_title>`\ ()
        - Title of the prompt based video, generated from an LLM. If not available, we generate it from the prompt
      * - :py:obj:`prepare_build <prompt_based_video.PromptBasedVideo.prepare_build>`\ (build_settings)
        - Generate the actual inner video


   .. rubric:: Members

   .. py:method:: compose(build_settings: vikit.video.video.VideoBuildSettings)
      :async:


      Compose the inner composite video

      Params:
          - build_settings: allow some customization

      :returns: The inner composite video


   .. py:method:: get_title()

      Title of the prompt based video, generated from an LLM. If not available, we generate it from the prompt


   .. py:method:: prepare_build(build_settings=VideoBuildSettings())
      :async:


      Generate the actual inner video

      Params:
          - build_settings: allow some customization

      :returns: The current instance







