
GeneralBuildSettings
====================

.. py:module:: GeneralBuildSettings


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`GeneralBuildSettings <GeneralBuildSettings.GeneralBuildSettings>`
     - General build settings for the video generation




Classes
-------

.. py:class:: GeneralBuildSettings(delete_interim_files: bool = False, run_async: bool = False, test_mode: bool = False, output_path: str = None)

   General build settings for the video generation

   The settings are:
   - delete_interim_files: whether to delete the intermediate video files, first and last frames
   - run_async: whether to run the video generation in async mode, to boost reactivity and performance of the application
   - test_mode: whether to run the video generation in local mode, to run local and fast tests


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`get_ml_models_gateway <GeneralBuildSettings.GeneralBuildSettings.get_ml_models_gateway>`\ ()
        - Handy function to get the ML models gateway from the buildsettings, as it is used in many places


   .. rubric:: Members

   .. py:method:: get_ml_models_gateway()

      Handy function to get the ML models gateway from the buildsettings, as it is used in many places
      like a context







