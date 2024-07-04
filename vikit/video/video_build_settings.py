from vikit.common import GeneralBuildSettings
from vikit.prompt.recorded_prompt import RecordedPrompt
from vikit.music import MusicBuildingContext


class VideoBuildSettings(GeneralBuildSettings.GeneralBuildSettings):
    def __init__(
        self,
        delete_interim_files: bool = False,
        run_async: bool = False,
        test_mode: bool = True,
        expected_length: float = None,  # The expected length in seconds of the video, will be used when actually building the video
        include_audio_read_subtitles: bool = False,  # Include subtitles in the final video
        prompt: RecordedPrompt = None,  # Include subtitles in the final video and fit videos to match the prompt subtitles timelines
        generate_from_llm_keyword: bool = False,  # Ask to generate the video by generating keywords from a LLM Prompt
        generate_from_llm_prompt: bool = True,
        interpolate: bool = True,  # Ask to interpolate the video
        music_building_context: MusicBuildingContext = MusicBuildingContext(),
        target_path: str = None,  # The path where the video will be saved, could be local or remote (i.e. a cloud bucket or a streaming service)
    ):

        super().__init__(
            delete_interim_files=delete_interim_files,
            run_async=run_async,
            test_mode=test_mode,
            output_path=target_path,
        )

        self.expected_length = expected_length
        self.include_audio_subtitles = include_audio_read_subtitles
        self.prompt = prompt
        self.generate_from_llm_keyword = generate_from_llm_keyword
        self.generate_from_llm_prompt = generate_from_llm_prompt
        self.music_building_context = music_building_context
        self.interpolate = interpolate
