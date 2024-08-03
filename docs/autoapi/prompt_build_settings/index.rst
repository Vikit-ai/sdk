
prompt_build_settings
=====================

.. py:module:: prompt_build_settings


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`PromptBuildSettings <prompt_build_settings.PromptBuildSettings>`
     - \-




Classes
-------

.. py:class:: PromptBuildSettings(delete_interim_files: bool = False, test_mode: bool = True, ml_models_gateway: vikit.gateways.ML_models_gateway.MLModelsGateway = None, generate_from_llm_keyword: bool = False, generate_from_llm_prompt: bool = True, **kwargs)

   Bases: :py:obj:`vikit.common.GeneralBuildSettings.GeneralBuildSettings`


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`get_ml_models_gateway <prompt_build_settings.PromptBuildSettings.get_ml_models_gateway>`\ ()
        - Handy function to get the ML models gateway from the buildsettings, as it is used in many places


   .. rubric:: Members

   .. py:method:: get_ml_models_gateway()

      Handy function to get the ML models gateway from the buildsettings, as it is used in many places
      like a context







