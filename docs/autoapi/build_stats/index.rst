
build_stats
===========

.. py:module:: build_stats


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`BuildStats <build_stats.BuildStats>`
     - Stores and help measure the time taken to build a video.




Classes
-------

.. py:class:: BuildStats(video: vikit.video.video = None)

   Stores and help measure the time taken to build a video.

   We do store the related video id and its top parent video id to help filter out the stats.

   Used to keep telemetry stats too, which means we will serialize this class and send it to the telemetry platform.


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`start <build_stats.BuildStats.start>`\ ()
        - \-
      * - :py:obj:`stop <build_stats.BuildStats.stop>`\ ()
        - \-


   .. rubric:: Members

   .. py:method:: start()

   .. py:method:: stop()






