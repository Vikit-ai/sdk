
handler
=======

.. py:module:: handler


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`Handler <handler.Handler>`
     - Helper class that provides a standard way to create an ABC using




Classes
-------

.. py:class:: Handler

   Bases: :py:obj:`abc.ABC`

   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`execute_async <handler.Handler.execute_async>`\ (object_to_transform, \*\*kwargs)
        - :summarylabel:`abc` Execute the handler asynchronously.


   .. rubric:: Members

   .. py:method:: execute_async(object_to_transform, **kwargs)
      :abstractmethod:

      :async:


      Execute the handler asynchronously.

      :param object_to_transforms: The object to transform prompt to process. It usually includes build settings
      :param \*\*kwargs: Additional arguments

      :returns: the transformed object_to_transforms







