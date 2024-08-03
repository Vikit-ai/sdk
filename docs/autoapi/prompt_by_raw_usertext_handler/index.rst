
prompt_by_raw_usertext_handler
==============================

.. py:module:: prompt_by_raw_usertext_handler


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`PromptByRawUserTextHandler <prompt_by_raw_usertext_handler.PromptByRawUserTextHandler>`
     - \-




Classes
-------

.. py:class:: PromptByRawUserTextHandler

   Bases: :py:obj:`vikit.common.handler.Handler`


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`execute_async <prompt_by_raw_usertext_handler.PromptByRawUserTextHandler.execute_async>`\ (text_prompt, \*\*kwargs)
        - Process the text prompt to generate a better one more suited to generate a video,  and a title


   .. rubric:: Members

   .. py:method:: execute_async(text_prompt: str, **kwargs)
      :async:


      Process the text prompt to generate a better one more suited to generate a video,  and a title
      summarizing the prompt.

      :param prompt: The prompt to generate the keywords from
      :type prompt: str
      :param build_settings: The build settings
      :type build_settings: PromptBuildSettings

      :returns: a string containing a list of keywords to be used for video generation







