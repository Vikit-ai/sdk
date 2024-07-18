file_tools
==========

.. py:module:: file_tools


Functions
---------

.. autoapisummary::

   file_tools.create_non_colliding_file_name
   file_tools.get_canonical_name
   file_tools.get_max_filename_length
   file_tools.get_max_remote_path_length
   file_tools.get_safe_filename
   file_tools.get_validated_path


Module Contents
---------------

.. py:function:: create_non_colliding_file_name(canonical_name: str = None, extension: str = 'xyz')

   Transforms the filename to prevent collisions zith other files,
   by adding a UUID as suffix

   params:
       canonical_name: a name used as the target file name prefix
       extension: the extension of the file

   return: the non-colliding name


.. py:function:: get_canonical_name(file_path: str)

   Get the canonical name of a file, without the extension


.. py:function:: get_max_filename_length(path='.')

   Fit the file name to a certain length, by removing the last characters if it is too long

   params:
   file_name: the file name to be fitted

   return: file name max length.


.. py:function:: get_max_remote_path_length()

   Get the maximum length of a remote path


.. py:function:: get_safe_filename(filename)

.. py:function:: get_validated_path(path: Optional[Union[str, os.PathLike]]) -> dict

   Validate the path and return its type

   Args:
       path (str, os.PathLike): The path to validate

   Returns:
       dict: The path type and the path itself


