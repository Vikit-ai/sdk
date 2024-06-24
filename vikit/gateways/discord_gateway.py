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
