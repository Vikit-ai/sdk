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
