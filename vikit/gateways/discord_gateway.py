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

from vikit.common.secrets import get_discord_api_key


def post_message(message, video_name):
    url = "https://discord.com/api/v10/channels/1226516037525311502/messages"

    # For authorization, you can use either your bot token
    headers = {
        "Authorization": "Bot MTIyNjgxNTk5ODI2NzYyNTUwMg.GD6lhK.BJ0SZRBFkdI2DTfdtlYDfS3QtjItYCKsDB2Qjk"
    }

    json = {
        "content": message
        + " https://storage.googleapis.com/aivideoscreated/"
        + video_name
        + " <@"
        + get_discord_api_key()
        + ">",
    }

    r = requests.post(url, headers=headers, json=json)
    logger.debug(f"Discord Gateway posting message: {r.content}")
