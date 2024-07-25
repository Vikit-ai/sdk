# Copyright 2024 Vikit.ai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from os import getenv, path

from dotenv import load_dotenv
from loguru import logger

# Get the absolute path to the directory this file is in.
dir_path = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
env_file = path.join(dir_path, ".env.secrets." + getenv("CONFIG_ENVIRONMENT", "dev"))
if not path.exists(env_file):
    logger.warning(f"Secrets file {env_file} does not exist")
else:
    load_dotenv(dotenv_path=env_file)


def get_sendinblue_api_key():
    sendinblue_api_key = getenv("SENDINBLUE_API_KEY", "dev")
    if sendinblue_api_key is None:
        raise Exception("SENDINBLUE_API_KEY is not set")
    return sendinblue_api_key


def get_openai_whisper_api_key():
    openai_whisper_api_key = getenv("OPENAI_WHISPER_MODEL_ID", "dev")
    if openai_whisper_api_key is None:
        raise Exception("OPENAI_WHISPER_MODEL_ID is not set")
    return openai_whisper_api_key


def get_replicate_api_token():
    replicate_api_key = getenv("REPLICATE_API_TOKEN", "dev")
    if replicate_api_key is None:
        raise Exception("REPLICATE_API_TOKEN is not set")
    return replicate_api_key


def get_vikit_api_token():
    replicate_api_key = getenv("VIKIT_API_TOKEN", "dev")
    if replicate_api_key is None:
        raise Exception("VIKIT_API_TOKEN is not set")
    return replicate_api_key


def get_eleven_labs_api_key():
    eleven_labs_api_key = getenv("ELEVEN_LABS_KEY", "dev")
    if eleven_labs_api_key is None:
        raise Exception("ELEVEN_LABS_KEY is not set")
    return eleven_labs_api_key


def get_discord_api_key():
    discord_api_key = getenv("DISCORD_API_KEY", "dev")
    if discord_api_key is None:
        raise Exception("DISCORD_API_KEY is not set")
    return discord_api_key
