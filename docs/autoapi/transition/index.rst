transition
==========

.. py:module:: transition


Attributes
----------

.. autoapisummary::

   transition.TIMEOUT


Classes
-------

.. autoapisummary::

   transition.Transition


Functions
---------

.. autoapisummary::

   transition.web_url_exists
   transition.url_exists


Module Contents
---------------

.. py:data:: TIMEOUT
   :value: 5


.. py:function:: web_url_exists(url)

   Check if a URL exists on the web


.. py:function:: url_exists(url: str)

   Check if a URL exists somewhere on the internet or locally

   Args:
       url (str): The URL to check

   Returns:
       bool: True if the URL exists, False otherwise



.. py:class:: Transition(source_video: vikit.video.video.Video, target_video: vikit.video.video.Video)

   Bases: :py:obj:`vikit.video.video.Video`

   Base class for transitions between videos.


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`get_title <transition.Transition.get_title>`\ ()
        - \-
      * - :py:obj:`get_file_name_by_state <transition.Transition.get_file_name_by_state>`\ (build_settings)
        - Get the file name of the video
      * - :py:obj:`build <transition.Transition.build>`\ (build_settings)
        - \-


   .. rubric:: Members

   .. py:method:: get_title()

   .. py:method:: get_file_name_by_state(build_settings: vikit.video.video_build_settings.VideoBuildSettings)

      Get the file name of the video

      Returns:
          str: The file name of the video


   .. py:method:: build(build_settings: vikit.video.video_build_settings.VideoBuildSettings = None)


