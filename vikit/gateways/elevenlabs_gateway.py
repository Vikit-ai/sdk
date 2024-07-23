from loguru import logger

import aiohttp
import aiofiles

from vikit.common.config import get_elevenLabs_url
from vikit.common.secrets import get_eleven_labs_api_key


async def generate_mp3_from_text_async(text, target_file):
    CHUNK_SIZE = 1024
    # TODO: See if we can play with chunk size to optimize performance

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": get_eleven_labs_api_key(),
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            get_elevenLabs_url(), json=payload, headers=headers
        ) as response:
            if response.status == 200:
                async with aiofiles.open(target_file, "wb") as f:
                    logger.debug(f"Writing mp3 to {target_file}")
                    async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                        if chunk:
                            await f.write(chunk)
                    logger.debug("mp3 sucessfully written")
            else:
                logger.error(f"Failed to fetch audio: {response.status}")
