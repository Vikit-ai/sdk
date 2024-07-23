import aiohttp
import aiofiles

from loguru import logger

from vikit.common.decorators import log_function_params


@log_function_params
async def download_file(url, filename):
    async with aiohttp.ClientSession() as session:
        logger.debug(f"Downloading file from {url} to {filename}")
        async with session.get(url) as response:
            if response.status == 200:
                # Utilisez aiofiles pour écrire le contenu de manière asynchrone
                async with aiofiles.open(filename, "wb") as f:
                    while (
                        True
                    ):  # Lire le contenu par morceaux pour ne pas surcharger la mémoire
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        await f.write(chunk)
                return filename
