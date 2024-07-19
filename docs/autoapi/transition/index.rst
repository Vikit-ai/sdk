
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


.. list-table:: Function
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`url_exists <transition.url_exists>`\ (url)
     - Check if a URL exists somewhere on the internet or locally
   * - :py:obj:`web_url_exists <transition.web_url_exists>`\ (url)
     - Check if a URL exists on the web


.. list-table:: Attributes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`TIMEOUT <transition.TIMEOUT>`
     - \-


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

      * - :py:obj:`build <transition.Transition.build>`\ (build_settings)
        - \-
      * - :py:obj:`get_file_name_by_state <transition.Transition.get_file_name_by_state>`\ (build_settings)
        - Get the file name of the video
      * - :py:obj:`get_title <transition.Transition.get_title>`\ ()
        - \-


   .. rubric:: Members

   .. py:method:: build(build_settings: vikit.video.video_build_settings.VideoBuildSettings = None)

   .. py:method:: get_file_name_by_state(build_settings: vikit.video.video_build_settings.VideoBuildSettings)

      Get the file name of the video

      :returns: The file name of the video
      :rtype: str


   .. py:method:: get_title()



Functions
---------
.. py:function:: url_exists(url: str)

   Check if a URL exists somewhere on the internet or locally

   :param url: The URL to check
   :type url: str

   :returns: True if the URL exists, False otherwise
   :rtype: bool


.. py:function:: web_url_exists(url)

   Check if a URL exists on the web



Attributes
----------
.. py:data:: TIMEOUT
   :value: 5




