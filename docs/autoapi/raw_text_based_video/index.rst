
raw_text_based_video
====================

.. py:module:: raw_text_based_video


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`RawTextBasedVideo <raw_text_based_video.RawTextBasedVideo>`
     - Generates a video from raw text prompt, i.e. very similar to calling a mainstream video generation platform.




Classes
-------

.. py:class:: RawTextBasedVideo(raw_text_prompt: str = None, title=None)

   Bases: :py:obj:`vikit.video.video.Video`

   Generates a video from raw text prompt, i.e. very similar to calling a mainstream video generation platform.
   This is currently the smallest building block available in the SDK, aimed to be used when you want more control
   over the video generation process.


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`build <raw_text_based_video.RawTextBasedVideo.build>`\ (build_settings, excluded_words)
        - Generate the actual inner video
      * - :py:obj:`get_title <raw_text_based_video.RawTextBasedVideo.get_title>`\ ()
        - \-


   .. rubric:: Members

   .. py:method:: build(build_settings=VideoBuildSettings(), excluded_words='')

      Generate the actual inner video

      Params:
          - build_settings: allow some customization
          - generate_from_keywords: generate the video out of keywords infered from the given prompt, and using an LLM.
          If False, we will generate an enhanced prompt and generate the video out of it
          - excluded_words: words to exclude from the prompt. This is used so as to prevent too much repetition across distant video scenes

      :returns: The current instance


   .. py:method:: get_title()






