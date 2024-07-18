from loguru import logger

from vikit.prompt.text_prompt_builder import TextPromptBuilder
from vikit.prompt.recorded_prompt_builder import RecordedPromptBuilder
from vikit.prompt.text_prompt_subtitles_extractor import TextPromptSubtitlesExtractor
from vikit.prompt.recorded_prompt_subtitles_extractor import (
    RecordedPromptSubtitlesExtractor,
)
from vikit.common.decorators import log_function_params
import vikit.common.config as config
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.prompt.building.prompt_building_handler import PromptBuildingHandler
from vikit.prompt.text_prompt import TextPrompt
from vikit.prompt.prompt_build_settings import PromptBuildSettings

from vikit.prompt.building.handlers.prompt_by_keywords_handler import (
    PromptByKeywordsHandler,
)
from vikit.prompt.building.handlers.prompt_by_raw_usertext_handler import (
    PromptByRawUserTextHandler,
)


class PromptFactory:
    """
    Prompt factory helps getting the right sub class of Prompt depending on
    the input provided. We use the right builder class to make it clear of the operations
    required to build each type of prompt and optimise it

    This is also useful to simplify unit testing of prompts as we will inject custom made Prompt objects
    instead of letting builders run some complex stuff involving external services
    """

    def __init__(
        self,
        ml_gateway: MLModelsGateway = None,
        prompt_build_settings: PromptBuildSettings = None,
    ):
        """
        Constructor of the prompt factory

        Args:
            ml_gateway: The ML Gateway to use to generate the prompt from the audio file

        """
        prompt_build_settings = (
            prompt_build_settings if prompt_build_settings else PromptBuildSettings()
        )
        if ml_gateway:
            self._ml_gateway = ml_gateway
        else:
            self._ml_gateway = prompt_build_settings.get_ml_models_gateway()

    @log_function_params
    async def create_prompt_from_text(
        self,
        prompt_text: str = None,
        generate_recording: bool = True,
    ):
        """
        Create a prompt object from a prompt text by possibly creating
        a recorded  audio file using a ML Model if asked to do so

        args:
            - prompt_text: the text of the prompt
            - generate_recording: a boolean to indicate if we should generate a recording from the text
            before extracting subtitles

        returns:
            self
        """
        if not prompt_text:
            raise ValueError("The prompt text is not provided")
        if len(prompt_text) == 0:
            raise ValueError("The prompt text is empty")
        extractor = None
        if generate_recording:
            await self._ml_gateway.generate_mp3_from_text_async(
                prompt_text=prompt_text, target_file=config.get_prompt_mp3_file_name()
            )

            extractor = RecordedPromptSubtitlesExtractor()
            subs = extractor.extract_subtitles_async(
                recorded_prompt_file_path=config.get_prompt_mp3_file_name(),
                ml_models_gateway=self._ml_gateway,
            )
            merged_subs = extractor.merge_short_subtitles(
                subs, min_duration=config.get_subtitles_min_duration()
            )

            prompt = (
                TextPromptBuilder()
                .set_prompt_text(prompt_text)
                .set_subtitles(merged_subs)
                .build()
            )
            prompt.recorded_audio_prompt_path = config.get_prompt_mp3_file_name()
        else:
            extractor = TextPromptSubtitlesExtractor()
            subs = extractor.extract_subtitles(prompt_text)
            merged_subs = extractor.merge_short_subtitles(
                subs, min_duration=config.get_subtitles_min_duration()
            )
            prompt = (
                TextPromptBuilder()
                .set_prompt_text(prompt_text)
                .set_subtitles(merged_subs)
                .build()
            )

        return prompt

    @log_function_params
    async def create_prompt_from_audio_file(
        self,
        recorded_audio_prompt_path: str = None,
    ):
        """
        Create a prompt object from a recorded audio file

        args:
            - recorded_audio_prompt_path: the path to the recorded audio file

        returns:
            self

        """
        extractor = RecordedPromptSubtitlesExtractor()

        subs = await extractor.extract_subtitles_async(
            recorded_audio_prompt_path, ml_models_gateway=self._ml_gateway
        )
        merged_subs = extractor.merge_short_subtitles(
            subs, min_duration=config.get_subtitles_min_duration()
        )
        text = extractor.build_subtitles_as_text_tokens(merged_subs)
        prompt = RecordedPromptBuilder().set_subtitles(merged_subs).set_text(text)
        prompt = await prompt.convert_recorded_audio_prompt_path(
            recorded_audio_prompt_path
        )

        return prompt.build()

    async def get_reengineered_prompt_from_text(
        self, prompt: str, prompt_build_settings: PromptBuildSettings
    ) -> TextPrompt:
        """
        Get a reengineered prompt from a text prompt, using build settings
        to guide how we should build the prompt

        Args:
            prompt (str): The text prompt

        Returns:
            Prompt: The prompt object
        """
        text_prompt = TextPromptBuilder().set_prompt_text(prompt).build()
        handler_chain = self.get_prompt_handler_chain(prompt_build_settings)
        if len(handler_chain) == 0:
            return text_prompt
        else:
            text_prompt, additional_args = await handler_chain[0].execute_async(
                prompt=text_prompt, build_settings=prompt_build_settings
            )
            if additional_args:
                text_prompt.extended_fields = additional_args

        return text_prompt

    def get_prompt_handler_chain(
        self, prompt_build_settings: PromptBuildSettings
    ) -> list[PromptBuildingHandler]:
        """
        Get the handler chain of the Prompt. Can includes handlers to prepare
        the prompt text by adding more verbosity, or to filter ofensing words, limit
        the prompt length, etc

        Args:
            build_settings (PromptBuildSettings): The settings to use for building the prompt

        Returns:
            list: The list of handlers to use for building the video
        """
        handlers = []
        if prompt_build_settings.generate_from_llm_keyword:
            handlers.append(PromptByKeywordsHandler())
        if prompt_build_settings.generate_from_llm_prompt:
            handlers.append(PromptByRawUserTextHandler())

        return handlers
