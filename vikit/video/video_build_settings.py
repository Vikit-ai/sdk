from vikit.common import GeneralBuildSettings
from vikit.prompt.prompt import Prompt
from vikit.music_building_context import MusicBuildingContext


class VideoBuildSettings(GeneralBuildSettings.GeneralBuildSettings):
    def __init__(
        self,
        delete_interim_files: bool = False,
        run_async: bool = True,
        test_mode: bool = True,
        target_model_provider: str = None,
        expected_length: float = None,
        include_read_aloud_prompt: bool = False,
        prompt: Prompt = None,
        generate_from_llm_keyword: bool = False,
        generate_from_llm_prompt: bool = True,
        generate_from_image_prompt: bool = True,
        interpolate: bool = True,
        music_building_context: MusicBuildingContext = MusicBuildingContext(),
        target_path: str = None,
        output_video_file_name: str = None,
    ):
        """
        VideoBuildSettings class constructor

        params:
            delete_interim_files: bool : Whether to delete the interim files generated during the video building process
            run_async: bool : Whether to run the video building process asynchronously
            test_mode: bool : Whether to run the video building process in test mode

            target_model_provider: str : The target model provider, in case you don't want to use the one defined by Vikit for each scene of the video
            Could be vikit, haiper, stability-ai, videocrafter, etc.

            expected_length:  The expected length in seconds of the video, will be used when actually building the video
            include_read_aloud_prompt:  Include a synthetic voice that reads the prompts in the final video
            prompt: Prompt : Include subtitles in the final video and fit videos to match the prompt subtitles timelines
            generate_from_llm_keyword : Ask to generate the video by generating keywords from a LLM Prompt
            generate_from_llm_prompt : Ask to generate the video by generating prompts from a LLM Prompt
            generate_from_image_prompt : Ask to generate the video by generating prompts from an image
            interpolate : Ask to interpolate the video
        """

        super().__init__(
            delete_interim_files=delete_interim_files,
            run_async=run_async,
            test_mode=test_mode,
            output_path=target_path,
            output_file_name=output_video_file_name,
        )

        self.expected_length = expected_length
        self.include_read_aloud_prompt = include_read_aloud_prompt
        self.prompt = prompt
        self.generate_from_llm_keyword = generate_from_llm_keyword
        self.generate_from_llm_prompt = generate_from_llm_prompt
        self.generate_from_image_prompt = generate_from_image_prompt
        self.music_building_context = music_building_context
        self.interpolate = interpolate
        self.target_model_provider = target_model_provider
