from loguru import logger

from vikit.prompt.text_prompt_builder import TextPromptBuilder
from vikit.prompt.recorded_prompt_builder import RecordedPromptBuilder
from vikit.prompt.text_prompt_subtitles_extractor import TextPromptSubtitlesExtractor
from vikit.prompt.recorded_prompt_subtitles_extractor import (
    RecordedPromptSubtitlesExtractor,
)
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
from vikit.wrappers.ffmpeg_wrapper import get_media_duration


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
        logger.debug(f"Creating prompt from text: {prompt_text}")
        if generate_recording:
            # calling a model like Whisper from openAI
            await self._ml_gateway.generate_mp3_from_text_async(
                prompt_text=prompt_text,
                target_file_name=config.get_prompt_mp3_file_name(),
            )

            extractor = RecordedPromptSubtitlesExtractor()
            subs = await extractor.extract_subtitles_async(
                recorded_prompt_file_path=config.get_prompt_mp3_file_name(),
                ml_models_gateway=self._ml_gateway,
            )
            merged_subs = extractor.merge_short_subtitles(  # merge short subtitles into larger ones
                subs, min_duration=config.get_subtitles_min_duration()
            )

            prompt = (
                RecordedPromptBuilder()
                .set_prompt_text(prompt_text)
                .set_subtitles(merged_subs)
                .set_audio_recording(config.get_prompt_mp3_file_name())
                .set_duration(get_media_duration(config.get_prompt_mp3_file_name()))
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
        prompt = (
            RecordedPromptBuilder().set_subtitles(merged_subs).set_prompt_text(text)
        )
        prompt = await prompt.convert_recorded_audio_prompt_path_to_mp3(
            recorded_audio_prompt_path
        )

        return prompt.build()

    async def get_reengineered_prompt_from_text(
        self,
        prompt: str,
        prompt_build_settings: PromptBuildSettings,
        duration: float = 0,
    ) -> TextPrompt:
        """
        Get a reengineered prompt from a text prompt, using build settings
        to guide how we should build the prompt

        Args:
            prompt (str): The text prompt

        Returns:
            Prompt: The prompt object
        """
        handler_chain = self.get_prompt_handler_chain(prompt_build_settings)
        if len(handler_chain) == 0:
            return prompt
        else:
            for handler in handler_chain:
                text_prompt, video_suggested_title = await handler.execute_async(
                    text_prompt=prompt, prompt_build_settings=prompt_build_settings
                )

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
