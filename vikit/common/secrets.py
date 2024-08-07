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
from sys import exit
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


def get_app_analytics_api_key() -> str:
    app_analytics_api_key = getenv("VIKIT_APP_ANALYTICS_PROJECT_ID", None)
    if app_analytics_api_key is None:
        raise Exception("VIKIT_APP_ANALYTICS_PROJECT_ID is not set")
    return app_analytics_api_key


def get_telemetry_api_key() -> str:
    telemetry_key = getenv("VIKIT_TELEMETRY_API_TOKEN", None)
    if telemetry_key is None:
        raise Exception("VIKIT_TELEMETRY_API_TOKEN is not set")
    return telemetry_key


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
    replicate_api_key = getenv("VIKIT_API_TOKEN", None)
    if replicate_api_key is None:
        logger.error(
            "VIKIT_API_TOKEN is not set. If you do not have a token, get one at https://vikit.ai/#/platform and add it to your .env.secrets file. Restart and rerun the file if you are working in a Colab or Jupyter notebook."
        )
        exit(1)
    return replicate_api_key


def get_eleven_labs_api_key():
    eleven_labs_api_key = getenv("ELEVEN_LABS_KEY", "dev")
    if eleven_labs_api_key is None:
        raise Exception("ELEVEN_LABS_KEY is not set")
    return eleven_labs_api_key


def has_eleven_labs_api_key():
    eleven_labs_api_key = getenv("ELEVEN_LABS_KEY", "dev")
    return eleven_labs_api_key != "dev"
