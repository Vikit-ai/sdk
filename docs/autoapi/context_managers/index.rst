
context_managers
================

.. py:module:: context_managers


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`Step <context_managers.Step>`
     - This class is a context manager to print a message with an emoji before and after a block of code
   * - :py:obj:`WorkingFolderContext <context_managers.WorkingFolderContext>`
     - This class is a context manager to change the working directory to the one specified




Classes
-------

.. py:class:: Step(msg='', emoji='')

   This class is a context manager to print a message with an emoji before and after a block of code
   Maybe deprecated in the near future




.. py:class:: WorkingFolderContext(path=None, delete_on_exit=False, mark: str = None)

   This class is a context manager to change the working directory to the one specified
   in the constructor







