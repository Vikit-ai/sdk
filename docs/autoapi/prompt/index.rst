prompt
======

.. py:module:: prompt


Classes
-------

.. autoapisummary::

   prompt.Prompt


Module Contents
---------------


.. py:class:: Prompt(ml_gateway: vikit.gateways.ML_models_gateway.MLModelsGateway = None)

   Bases: :py:obj:`abc.ABC`

   A class to represent a prompt, a user written prompt, a prompt
   generated from an audio file, or one sent or received from an LLM.

   This class is going to be used as a base class for new type of prompts as
   they are accepted by LLM's, like an image, a video, or an embedding...


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`get_duration <prompt.Prompt.get_duration>`\ ()
        - Returns the duration of the prompt in seconds. This is not ideal and should be used only if


   .. rubric:: Members

   .. py:method:: get_duration() -> float

      Returns the duration of the prompt in seconds. This is not ideal and should be used only if
      we don't have the recording of the prompt.



