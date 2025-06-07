import asyncio
from vikit.wrappers.ffmpeg_wrapper import (
    concatenate_videos,
)  # adapte selon le nom de ton fichier


async def main():
    # Test concaténation avec des fichiers exemples
    result = await concatenate_videos(
        ["~/Downloads/small.mp4", "~/Downloads/test-media-with-short-speech.mp4"],
        target_file_name="output_test.mp4",
    )
    print(f"Video saved to: {result}")


if __name__ == "__main__":
    asyncio.run(main())
