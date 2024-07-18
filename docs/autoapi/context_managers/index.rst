context_managers
================

.. py:module:: context_managers


Classes
-------

.. autoapisummary::

   context_managers.WorkingFolderContext
   context_managers.Step


Module Contents
---------------


.. py:class:: WorkingFolderContext(path=None, delete_on_exit=False, mark: str = None)

   This class is a context manager to change the working directory to the one specified
   in the constructor




.. py:class:: Step(msg='', emoji='')

   This class is a context manager to print a message with an emoji before and after a block of code
   Maybe deprecated in the near future



