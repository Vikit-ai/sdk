import os

from vikit.prompt.text_prompt_builder import TextPromptBuilder
from vikit.prompt.recorded_prompt_builder import RecordedPromptBuilder
from vikit.prompt.text_prompt_subtitles_extractor import TextPromptSubtitlesExtractor
from vikit.prompt.recorded_prompt_subtitles_extractor import (
    RecordedPromptSubtitlesExtractor,
)
import vikit.gateways.elevenlabs_gateway as elevenlabs_gateway
from vikit.common.decorators import log_function_params
import vikit.common.config as config
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory


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
    ):
        """
        Constructor of the prompt factory

        Args:
            ml_gateway: The ML Gateway to use to generate the prompt from the audio file

        """
        if ml_gateway is None:
            self._ml_gateway = MLModelsGatewayFactory.get_ml_models_gateway_static(
                test_mode=True
            )
        else:
            self._ml_gateway = ml_gateway

    @log_function_params
    def create_prompt_from_text(
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
        if prompt_text is None:
            raise ValueError("The prompt text is not provided")
        if len(prompt_text) == 0:
            raise ValueError("The prompt text is empty")
        extractor = None

        if generate_recording:
            elevenlabs_gateway.generate_mp3_from_text(
                prompt_text, target_file=config.get_prompt_mp3_file_name()
            )
            assert os.path.exists(
                config.get_prompt_mp3_file_name()
            ), "The generated audio file does not exists"
            extractor = RecordedPromptSubtitlesExtractor()
            subs = extractor.extract_subtitles(
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
            prompt._recorded_audio_prompt_path = config.get_prompt_mp3_file_name()
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
    def create_prompt_from_audio_file(
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

        subs = extractor.extract_subtitles(
            recorded_audio_prompt_path, ml_models_gateway=self._ml_gateway
        )
        merged_subs = extractor.merge_short_subtitles(
            subs, min_duration=config.get_subtitles_min_duration()
        )
        text = extractor.build_subtitles_as_text_tokens(merged_subs)
        prompt = (
            RecordedPromptBuilder()
            .convert_recorded_audio_prompt_path(recorded_audio_prompt_path)
            .set_subtitles(merged_subs)
            .set_text(text)
            .build()
        )
        return prompt
