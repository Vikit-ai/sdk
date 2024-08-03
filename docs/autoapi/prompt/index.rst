
prompt
======

.. py:module:: prompt


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`Prompt <prompt.Prompt>`
     - A class to represent a prompt, a user written prompt, a prompt




Classes
-------

.. py:class:: Prompt

   Bases: :py:obj:`abc.ABC`

   A class to represent a prompt, a user written prompt, a prompt
   generated from an audio file, an image prompt, or one sent or received from an LLM.

   This class is going to be used as a base class for new type of prompts as
   they are accepted by LLM's, like a video, or an embedding...







