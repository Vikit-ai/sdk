
recorded_prompt_subtitles_extractor
===================================

.. py:module:: recorded_prompt_subtitles_extractor


Overview
--------

.. list-table:: Classes
   :header-rows: 0
   :widths: auto
   :class: summarytable

   * - :py:obj:`RecordedPromptSubtitlesExtractor <recorded_prompt_subtitles_extractor.RecordedPromptSubtitlesExtractor>`
     - A class to extract subtitles from a sound recording,




Classes
-------

.. py:class:: RecordedPromptSubtitlesExtractor

   Bases: :py:obj:`vikit.prompt.subtitle_extractor.SubtitleExtractor`

   A class to extract subtitles from a sound recording,
   merge short subtitles into longer ones, or extract them as text tokens

   Here is how we do it:
   - We extract the audio slice from the audio file and cap the duration of the slice to x seconds
   so that replicate can process it (today n = 300 seconds, i.e. 5minutes)
   - We save the generated subtitles to a temporary SRT file
   - We concatenate the temporary SRT files to a prompt wide srt file

   Yes this is kind of hacky, but it works for now.


   .. rubric:: Overview


   .. list-table:: Methods
      :header-rows: 0
      :widths: auto
      :class: summarytable

      * - :py:obj:`extract_subtitles_async <recorded_prompt_subtitles_extractor.RecordedPromptSubtitlesExtractor.extract_subtitles_async>`\ (recorded_prompt_file_path, ml_models_gateway)
        - Generate subtitles from a recorded audio file


   .. rubric:: Members

   .. py:method:: extract_subtitles_async(recorded_prompt_file_path, ml_models_gateway: vikit.gateways.ML_models_gateway.MLModelsGateway = None)
      :async:


      Generate subtitles from a recorded audio file

              inputs: NA
              returns: Subtitle Rip File object







