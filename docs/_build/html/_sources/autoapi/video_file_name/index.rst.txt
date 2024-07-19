
video_file_name
===============

.. py:module:: video_file_name


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`VideoFileName <video_file_name.VideoFileName>`
     - Class for Video file name manipulation.



.. list-table:: Attributes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`MANAGED_FEATURES <video_file_name.MANAGED_FEATURES>`
     - \-


Classes
-------

.. py:class:: VideoFileName(build_settings: vikit.video.video_build_settings.VideoBuildSettings, video_metadata: vikit.video.video_metadata.VideoMetadata, video_type: str = None, video_features: str = None, file_extension: str = 'mp4')

   Class for Video file name manipulation.

   A video file name is a string that represents the name of a video file.
   It respects a convention that is used to identify the video file easily

   Complementary metadata may exist in additional stores, however, the file name is the primary identifier
   and the bare minimum is here to simplify processing even if the metadata store is not available


   .. rubric:: Overview

   .. list-table:: Attributes
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`VIDEO_TITLE_MAX_LENGTH <video_file_name.VideoFileName.VIDEO_TITLE_MAX_LENGTH>`
        - \-


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`extract_features_as_string <video_file_name.VideoFileName.extract_features_as_string>`\ ()
        - Extract the features from the video features string
      * - :py:obj:`from_file_name <video_file_name.VideoFileName.from_file_name>`\ (file_name)
        - :summarylabel:`static` Parse a file name to extract the metadata
      * - :py:obj:`infer_features <video_file_name.VideoFileName.infer_features>`\ ()
        - Infer the features from the video features string
      * - :py:obj:`is_video_file_name <video_file_name.VideoFileName.is_video_file_name>`\ (file_name)
        - :summarylabel:`static` Check if a file name is a video file name
      * - :py:obj:`truncate <video_file_name.VideoFileName.truncate>`\ (gap)
        - Truncate the file name to fit the file system's limits


   .. rubric:: Members

   .. py:attribute:: VIDEO_TITLE_MAX_LENGTH
      :value: 30


   .. py:method:: extract_features_as_string()

      Extract the features from the video features string


   .. py:method:: from_file_name(file_name: str)
      :staticmethod:


      Parse a file name to extract the metadata

      params:
          file_name: The file name to parse

      :returns: The video file name object
      :rtype: VideoFileName


   .. py:method:: infer_features()

      Infer the features from the video features string

      In case unknown features are found, a warning is logged


   .. py:method:: is_video_file_name(file_name: str)
      :staticmethod:


      Check if a file name is a video file name

      params:
          file_name: The file name to check

      :returns: True if the file name is a video file name, False otherwise
      :rtype: bool


   .. py:method:: truncate(gap: int)

      Truncate the file name to fit the file system's limits

      params:
      gap: The gap between the file name's length and the file system's limits

      36 is the length of the UUID, 4 is the length of the file extension

      returns:
      str: The truncated file name





Attributes
----------
.. py:data:: MANAGED_FEATURES
   :value: 'dogrpvi'




