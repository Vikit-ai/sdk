import os
import asyncio
import aiohttp

import subprocess

from tenacity import retry, before_log, after_log, stop_after_attempt
from loguru import logger
from urllib.request import urlretrieve
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.prompt.prompt_cleaning import cleanse_llm_keywords
from vikit.common.decorators import log_function_params
from vikit.common.secrets import get_replicate_api_token, get_vikit_api_token
from vikit.common.config import get_nb_retries_http_calls
import requests
import base64
import json


os.environ["REPLICATE_API_TOKEN"] = get_replicate_api_token()
vikit_api_key = get_vikit_api_token()
vikit_backend_url = "https://videho.replit.app/models"
KEYWORDS_FORMAT_PROMPT = """' Just list the keywords in english language, separated by a coma, do not re-output the prompt. The answer should be a list of keywords and exactly match the following format:  'KEYWORD1, KEYWORD2, KEYWORD3, etc' where KEYWORD1 and the other ones are generated by you. The last word of your answer should be a summary of all the other keywords so I can generate a file name out of it, it should be limited to three words joined by the underscore character and you should only use characters compatible with filenames in the summary, so only standard alphanumerical characters. Don't prefix the summary with any special characters, just the words joined by underscores.'"""


class VikitGateway(MLModelsGateway):
    """
    A Gateway to interact with the Vikit API
    """

    def __init__(self):
        super().__init__()

    @log_function_params
    def generate_background_music_async(
        self, duration: int = 3, prompt: str = None
    ) -> str:
        """
        Here we generate the music to add as background music

        Args:
            - duration: int - the duration of the music in seconds
            - prompt: str - the prompt to generate the music from

        Returns:
            - str: the path to the generated music
        """
        assert (
            duration < 300
        ), "The duration of the music should be less than 300 seconds"

        outputLLM = asyncio.run(self.get_music_generation_keywords_async(prompt))
        logger.debug(f"outputLLM: {outputLLM}")

        # je veux le dernier mot de la liste de mots générés pour le nom du fichier
        prompt_based_music_file_name = str(outputLLM.split()[-1:][0]) + ".mp3"
        logger.debug(f"prompt_based_music_file_name: {prompt_based_music_file_name}")
        title_length = len(prompt_based_music_file_name)  # remove the .mp3 extension

        # Then we generate the music
        clean_prompt_without_title = outputLLM[:-title_length]
        logger.debug(f"Clean GPT Prompt : {clean_prompt_without_title}")
        output_music_link = self.compose_music_from_text(
            clean_prompt_without_title, duration=duration
        )

        logger.debug("Downloading the generated music")
        gen_music_file_path = urlretrieve(
            output_music_link, prompt_based_music_file_name
        )[0]
        lowered_music_filename = f"lowered_{prompt_based_music_file_name}"

        logger.debug("Lowering the volume of the music")
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                gen_music_file_path,
                "-filter_complex",
                "[a]loudnorm,volume=0.2",
                lowered_music_filename,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result.check_returncode()

        return lowered_music_filename

    @retry(
        stop=stop_after_attempt(get_nb_retries_http_calls()),
        reraise=True,
        before=before_log(logger, logger.level("TRACE").no),
        after=after_log(logger, logger.level("TRACE").no),
    )
    @log_function_params
    async def generate_seine_transition(self, source_image_path, target_image_path):
        """
        Generate a transition between two videos

        Args:
            index: The index of the video
            initial: Whether this is the initial video

        Returns:
            The link to the generated video
        """

        if source_image_path is None:
            raise AttributeError("The source image path is None")
        if target_image_path is None:
            raise AttributeError("The target image path is None")
        if not os.path.exists(source_image_path):
            raise FileNotFoundError(
                f"The source image path does not exist: {source_image_path}"
            )
        if not os.path.exists(target_image_path):
            raise FileNotFoundError(
                f"The target image path does not exist: {target_image_path}"
            )

        source_image_base64 = base64.b64encode(
            open(source_image_path, "rb").read()
        ).decode("ascii")
        target_image_base64 = base64.b64encode(
            open(target_image_path, "rb").read()
        ).decode("ascii")

        response = requests.post(
            vikit_backend_url,
            json={
                "key": vikit_api_key,
                "model": "leclem/seine-transition:6de45c0cdc731d9fdf73f1d7b9db6373089804b62f6f2c1e3c853f4f04e20566",
                "input": {
                    "image": "data:image/jpeg;base64," + source_image_base64,
                    "image2": "data:image/jpeg;base64," + target_image_base64,
                    "width": 512,
                    "height": 320,
                },
            },
        )

        return response.text

    ##################  Replicate API calls for Music keywords prompt and music gen  ##################

    @retry(
        stop=stop_after_attempt(get_nb_retries_http_calls()),
        reraise=True,
        before=before_log(logger, logger.level("TRACE").no),
        after=after_log(logger, logger.level("TRACE").no),
    )
    async def compose_music_from_text(self, prompt_text: str, duration: int):
        """
        Compose a music for a prompt text

        Args:
            prompt_text: The text prompt
            duration: The duration of the music

        Returns:
            The link to the generated music
        """
        assert prompt_text is not None
        assert duration is not None

        if duration < 1:
            raise AttributeError("The input duration is less than 1")
        if duration > 60:
            raise AttributeError("The input duration is greater than 60")
        if len(prompt_text) < 1:
            raise AttributeError("The input prompt text is empty")
        result_music_link = requests.post(
            vikit_backend_url,
            json={
                "key": vikit_api_key,
                "model": "meta/musicgen:b05b1dff1d8c6dc63d14b0cdb42135378dcb87f6373b0d3d341ede46e59e2b38",
                "input": {
                    "top_k": 250,
                    "top_p": 0,
                    "prompt": "Compose a background music allowing viewer to concentrate while still being engaging for a podcast video to be published on youtube that speaks about these topics: "
                    + prompt_text,
                    "duration": int(duration),
                    "temperature": 1,
                    "continuation": False,
                    "model_version": "stereo-large",
                    "output_format": "wav",
                    "continuation_start": 0,
                    "multi_band_diffusion": False,
                    "normalization_strategy": "peak",
                    "classifier_free_guidance": 3,
                },
            },
        ).text

        if result_music_link is None:
            raise AttributeError("The result music link is None")
        if len(result_music_link) < 1:
            raise AttributeError("The result music link is empty")

        return result_music_link

    @retry(
        stop=stop_after_attempt(get_nb_retries_http_calls()),
        reraise=True,
        before=before_log(logger, logger.level("TRACE").no),
        after=after_log(logger, logger.level("TRACE").no),
    )
    async def get_music_generation_keywords_async(self, text) -> str:
        """
        Generate keywords from a text using the Replicate API

        At the end of the resulting prompt we get 3 words that will be used to generate a file name out of
        the generated keywords

        Args:
            text: The text to generate keywords from

        Returns:
            A list of keywords
        """

        if text is None:
            text = "finaly there is no prompt so just unleash your own imagination"

        async with aiohttp.ClientSession() as session:
            payload = {
                "key": vikit_api_key,
                "model": "mistralai/mistral-7b-instruct-v0.2",
                "input": {
                    "top_k": 50,
                    "top_p": 0.9,
                    "prompt": """I want you to act as a english keyword generator for a music generation artificial
                                            intelligence program with the aim of generating a background music for a podcast video.
                                                Your job is to provide detailed and creative keywords that will inspire unique and interesting music
                                                from the AI for background music for a video. Keep in mind that the AI is capable of 
                                                understanding a wide range of language and can interpret abstract concepts, so feel free to be 
                                                as imaginative.  The more detailed and imaginative your keywords, the more interesting the
                                                    resulting music will be. Here is your prompt: '"""
                    + text
                    + KEYWORDS_FORMAT_PROMPT,
                    "temperature": 0.6,
                    "max_new_tokens": 1024,
                    "prompt_template": "<s>[INST] {prompt} [/INST] ",
                    "presence_penalty": 0,
                    "frequency_penalty": 0,
                },
            }

            async with session.post(vikit_backend_url, json=payload) as response:
                llm_keywords = await response.json()

        return cleanse_llm_keywords(llm_keywords.text)

    @retry(
        stop=stop_after_attempt(get_nb_retries_http_calls()),
        reraise=True,
        before=before_log(logger, logger.level("DEBUG").no),
        after=after_log(logger, logger.level("DEBUG").no),
    )
    async def interpolate(self, video):
        """
        Run some interpolation magic. This model may fail after timeout, so you
        should call it with retry logic

        Args:
            video: The video to interpolate

        Returns:
            a link to the interpolated video
        """
        if video is None:
            raise AttributeError("The input video is None")

        logger.debug(f"Video to interpolate {video}")

        return requests.post(
            vikit_backend_url,
            json={
                "key": vikit_api_key,
                "model": "pollinations/amt:6e03c945a24b2defe4576e35235b9c9c0120d81c9df58880c0b3832a5777cdcd",
                "input": {
                    "video": video,
                    "model_type": "amt-l",
                    "output_video_fps": 16,
                    "recursive_interpolation_passes": 2,
                },
            },
        ).text

    @retry(stop=stop_after_attempt(get_nb_retries_http_calls()), reraise=True)
    @log_function_params
    async def get_keywords_from_prompt(self, subtitleText, excluded_words: str = None):
        """
        Generates keywords from a subtitle text using the Replicate API.

        Args:
            A subtitle text

        Returns:
            A list of keywords generated by an LLM using the subtitle text

        """
        assert subtitleText is not None

        llm_keywords = requests.post(
            vikit_backend_url,
            json={
                "key": vikit_api_key,
                "model": "mistralai/mistral-7b-instruct-v0.2",
                "input": {
                    "top_k": 50,
                    "top_p": 0.9,
                    "prompt": "I want you to act as a english keyword generator for Midjourney's artificial intelligence program."
                    + "Your job is to provide detailed and creative descriptions that will inspire unique and interesting images from "
                    + "the AI for a video. Keep in mind that the AI is capable of understanding a wide range of language and can "
                    + "interpret abstract concepts, so feel free to be as imaginative and descriptive as possible. Don't repeat keywords. The more detailed "
                    + "and imaginative your keywords, the more interesting the resulting image will be. Here is the sentence from "
                    + "which to extract keywords: '"
                    ""
                    + subtitleText
                    + "'. Just list the keywords in english language, separated by a coma, do not re-output the prompt. "
                    + (
                        f" . Please avoid using these keywords: {excluded_words}"
                        if excluded_words
                        else ""
                    )
                    + KEYWORDS_FORMAT_PROMPT,
                    "temperature": 0.6,
                    "max_new_tokens": 32,
                    "prompt_template": "<s>[INST] {prompt} [/INST] ",
                    "presence_penalty": 0,
                    "frequency_penalty": 0,
                },
            },
        )

        clean_result = cleanse_llm_keywords(llm_keywords.text)
        title_from_keywords_as_tokens = clean_result.split()[-1:][0]

        # Transform the list of keywords into a single string, we do keep the final title within
        return clean_result, title_from_keywords_as_tokens

    @retry(stop=stop_after_attempt(get_nb_retries_http_calls()), reraise=True)
    @log_function_params
    async def get_enhanced_prompt(self, subtitleText):
        """
        Generates an enhanced prompt from an original one, probably written by a user or
        translated from an audio

        Args:
            A subtitle text

        Returns:
            A prompt enhanced by an LLM
        """

        outputLLM = requests.post(
            vikit_backend_url,
            json={
                "key": vikit_api_key,
                "model": "mistralai/mistral-7b-instruct-v0.2",
                "input": {
                    "top_k": 50,
                    "top_p": 0.9,
                    "prompt": "I want you to act as a one sentence prompt creator for Midjourney's artificial intelligence program. Your job is to provide one detailed and creative sentence that will inspire unique and interesting video from the AI to create. Keep in mind that the AI is capable of understanding a wide range of language and can interpret abstract concepts, so feel free to be as imaginative and descriptive as possible.  The more detailed and imaginative your description, the more interesting the resulting image will be. Here is the paragraph to summarize in one sentence that describes a scenario for a video: '"
                    + subtitleText
                    + "'. Just give me a short summary of what is said in a way that would make a good video. Please avoid speaking about anything related to text."
                    + "The last 3 words of your answer should be a summary of all the other keywords so I can generate a file name out of it",
                    "temperature": 0.6,
                    "max_new_tokens": 24,
                    "prompt_template": "<s>[INST] {prompt} [/INST] ",
                    "presence_penalty": 0,
                    "frequency_penalty": 0,
                },
            },
        )

        clean_result = cleanse_llm_keywords(outputLLM.text)
        title_from_keywords_as_tokens = clean_result.split()[-1:][0]

        # Transform the list of keywords into a single string, we do keep the final title within
        return clean_result, title_from_keywords_as_tokens

    @retry(stop=stop_after_attempt(get_nb_retries_http_calls()), reraise=True)
    @log_function_params
    async def get_subtitles(self, audiofile_path):
        # Obtain subtitles using Replicate API
        """
        Extract subtitles from an audio file using the Replicate API

        Args:
            i (int): The index of the audio slice

        Returns:
            subs: The subtitles obtained from the Replicate API

        """
        assert os.path.exists(
            audiofile_path
        ), f"The prompt recording file does not exist: {audiofile_path}"

        base64AudioFile = base64.b64encode(open(audiofile_path, "rb").read()).decode(
            "ascii"
        )

        subs = requests.post(
            vikit_backend_url,
            json={
                "key": vikit_api_key,
                "model": "cjwbw/whisper:b70a8e9dc4aa40bf4309285fbaefe3ed3d3a313f1f32ea61826fc64cdb4917a5",
                "input": {
                    "model": "base",
                    "translate": True,
                    "temperature": 0,
                    "transcription": "srt",
                    "suppress_tokens": "-1",
                    "logprob_threshold": -1,
                    "no_speech_threshold": 0.6,
                    "condition_on_previous_text": True,
                    "compression_ratio_threshold": 2.4,
                    "temperature_increment_on_fallback": 0.2,
                    "audio": "data:audio/mp3;base64," + base64AudioFile,
                },
            },
        )

        return json.loads(subs.text)

    @retry(stop=stop_after_attempt(get_nb_retries_http_calls()), reraise=True)
    async def generate_video(self, prompt: str):
        """
        Generate a video from the given prompt

        Args:
            prompt: The prompt to generate the video from

        returns:
                The link to the generated video
        """
        logger.debug(f"Generating video from prompt: {prompt}")
        output = requests.post(
            vikit_backend_url,
            json={
                "key": vikit_api_key,
                "model": "cjwbw/videocrafter:02edcff3e9d2d11dcc27e530773d988df25462b1ee93ed0257b6f246de4797c8",
                "input": {
                    "prompt": prompt,  # + ", 4k",
                    "save_fps": 8,
                    "ddim_steps": 50,
                    "unconditional_guidance_scale": 12,
                },
            },
        )

        return output.text
