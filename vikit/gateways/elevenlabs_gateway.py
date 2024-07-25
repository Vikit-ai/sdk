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

import requests
from loguru import logger

from vikit.common.config import get_elevenLabs_url
from vikit.common.secrets import get_eleven_labs_api_key


def generate_mp3_from_text(text, target_file):
    CHUNK_SIZE = 1024
    # TODO: See if we can play with chunk size to optimize performance

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": get_eleven_labs_api_key(),
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }

    response = requests.post(get_elevenLabs_url(), json=data, headers=headers)

    with open(target_file, "wb") as f:
        logger.debug(f"Writing mp3 to {target_file}")
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
