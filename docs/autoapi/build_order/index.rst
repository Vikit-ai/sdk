
build_order
===========

.. py:module:: build_order


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`is_composite_video <build_order.is_composite_video>`
     - Interface for composite videos, needed to prevent circular imports


.. list-table:: Function
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`get_lazy_dependency_chain_build_order <build_order.get_lazy_dependency_chain_build_order>`\ (video_tree, build_settings, already_added, video_build_order)
     - Get the first videos first build order



Classes
-------

.. py:class:: is_composite_video

   Bases: :py:obj:`abc.ABC`

   Interface for composite videos, needed to prevent circular imports


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`is_composite_video <build_order.is_composite_video.is_composite_video>`\ ()
        - :summarylabel:`abc` \-


   .. rubric:: Members

   .. py:method:: is_composite_video()
      :abstractmethod:




Functions
---------
.. py:function:: get_lazy_dependency_chain_build_order(video_tree: list[vikit.video.video.Video], build_settings: vikit.video.video_build_settings.VideoBuildSettings, already_added: set, video_build_order: list[vikit.video.video.Video] = [])

   Get the first videos first build order

   Here we generate the video in a lazy way, starting from the leaf composite and
   going up to the root composite as depency resolution is done

   So this is a width traversal of the video tree, but we go down the dependency chain too

   params:
       video_tree (list): The video tree to recurse on to parse the tree and get the build order
       build_settings: The build settings
       already_added (set): The set of already added videos

   :returns: The build order
   :rtype: list





