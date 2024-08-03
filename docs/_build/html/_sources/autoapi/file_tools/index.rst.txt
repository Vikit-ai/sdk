
file_tools
==========

.. py:module:: file_tools


Overview
--------


.. list-table:: Function
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`download_or_copy_file <file_tools.download_or_copy_file>`\ (url, local_path)
     - Download a file from a URL to a local file asynchronously
   * - :py:obj:`get_canonical_name <file_tools.get_canonical_name>`\ (file_path)
     - Get the canonical name of a file, without the extension
   * - :py:obj:`get_max_path_length <file_tools.get_max_path_length>`\ (path)
     - get the max file name for the current OS
   * - :py:obj:`get_max_remote_path_length <file_tools.get_max_remote_path_length>`\ ()
     - Get the maximum length of a remote path
   * - :py:obj:`get_path_type <file_tools.get_path_type>`\ (path)
     - Validate the path and return its type
   * - :py:obj:`get_safe_filename <file_tools.get_safe_filename>`\ (filename)
     - \-
   * - :py:obj:`is_valid_filename <file_tools.is_valid_filename>`\ (filename)
     - Check if the provided string is a valid filename for the local file system.
   * - :py:obj:`is_valid_path <file_tools.is_valid_path>`\ (path)
     - Check if the path is valid: could be a local path or a remote one
   * - :py:obj:`url_exists <file_tools.url_exists>`\ (url)
     - Check if a URL exists somewhere on the internet or locally. To be superseded by a more
   * - :py:obj:`web_url_exists <file_tools.web_url_exists>`\ (url)
     - Check if a URL exists on the web


.. list-table:: Attributes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`TIMEOUT <file_tools.TIMEOUT>`
     - \-



Functions
---------
.. py:function:: download_or_copy_file(url, local_path)
   :async:


   Download a file from a URL to a local file asynchronously

   :param url: The URL to download the file from
   :type url: str
   :param local_path: The filename to save the file to
   :type local_path: str

   :returns: The filename of the downloaded file
   :rtype: str


.. py:function:: get_canonical_name(file_path: str)

   Get the canonical name of a file, without the extension


.. py:function:: get_max_path_length(path='.')

   get the max file name for the current OS

   params:
       path: the file path

   return: file name max length.


.. py:function:: get_max_remote_path_length()

   Get the maximum length of a remote path


.. py:function:: get_path_type(path: Optional[Union[str, os.PathLike]]) -> dict

   Validate the path and return its type

   :param path: The path to validate
   :type path: str, os.PathLike,

   :returns: The path type and the path itself
             Path type can be local, http, https, s3, gs, None, undefined, error,
             error : message if the path is invalid, None if no error
   :rtype: dict


.. py:function:: get_safe_filename(filename)

.. py:function:: is_valid_filename(filename: str) -> bool

   Check if the provided string is a valid filename for the local file system.

   :param filename: The filename to check.
   :type filename: str

   :returns: True if valid, False otherwise.
   :rtype: bool


.. py:function:: is_valid_path(path: Optional[Union[str, os.PathLike]]) -> bool

   Check if the path is valid: could be a local path or a remote one
   (http, etc). We don't test the actual access and credentials at this stage,
   just the path fornat.

   :param path: The path to validate
   :type path: str, os.PathLike

   :returns: True if the path is valid, False otherwise
   :rtype: bool


.. py:function:: url_exists(url: str)

   Check if a URL exists somewhere on the internet or locally. To be superseded by a more
   versatile and unified library in the future.

   :param url: The URL to check
   :type url: str

   :returns: True if the URL exists, False otherwise
   :rtype: bool


.. py:function:: web_url_exists(url)

   Check if a URL exists on the web



Attributes
----------
.. py:data:: TIMEOUT
   :value: 10




