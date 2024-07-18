subtitle_extractor
==================

.. py:module:: subtitle_extractor


Classes
-------

.. autoapisummary::

   subtitle_extractor.SubtitleExtractor


Module Contents
---------------


.. py:class:: SubtitleExtractor

   A class to extract subtitles from a sound recording,
   merge short subtitles into longer ones, or extract them as text tokens


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`build_subtitles_as_text_tokens <subtitle_extractor.SubtitleExtractor.build_subtitles_as_text_tokens>`\ (subtitles)
        - Create blocks of subtitles
      * - :py:obj:`merge_short_subtitles <subtitle_extractor.SubtitleExtractor.merge_short_subtitles>`\ (subtitles, min_duration)
        - Merge subtitles which total duration is less than 7 seconds


   .. rubric:: Members

   .. py:method:: build_subtitles_as_text_tokens(subtitles) -> list[str]

      Create blocks of subtitles

      Args:
          subtitles: The subtitles to process

      returns:
          list of text tokens corresponding to the subtitles in some sort
          of human readeable format


   .. py:method:: merge_short_subtitles(subtitles, min_duration=7)

      Merge subtitles which total duration is less than 7 seconds



