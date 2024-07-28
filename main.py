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

import os
from vikit.prompt.prompt_build_settings import PromptBuildSettings
from vikit.video.composite_video import CompositeVideo
from vikit.video.seine_transition import SeineTransition
from vikit.video.video import VideoBuildSettings
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.raw_image_based_video import RawImageBasedVideo
from vikit.music_building_context import MusicBuildingContext
from loguru import logger  # type: ignore
from base64 import b64decode
import pandas as pd  # type: ignore
import argparse
import shutil
import asyncio
from vikit.prompt.prompt_factory import PromptFactory
from vikit.video.raw_image_based_video import RawImageBasedVideo
from vikit.prompt.prompt_factory import PromptFactory
from vikit.video.video import VideoBuildSettings
from vikit.common.context_managers import WorkingFolderContext
from vikit.music_building_context import MusicBuildingContext
import vikit.gateways.ML_models_gateway_factory as ML_models_gateway_factory
from vikit.video.prompt_based_video import PromptBasedVideo

logger.add("log.txt")


async def batch_raw_text_based_prompting(
    prompt_file: str, output_path: str, model_provider: str = "stabilityai"
):
    to_interpolate = True if model_provider == "videocrafter" else False
    video_build_settings = VideoBuildSettings(
        music_building_context=MusicBuildingContext(
            apply_background_music=False, generate_background_music=False
        ),
        test_mode=False,
        interpolate=to_interpolate,
        target_model_provider=model_provider,
    )
    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)
    for _, row in prompt_df.iterrows():
        prompt_text = row.iloc[1]
        output_file = f"./{output_path}{row.iloc[0]}.mp4"
        print(f"generating video from prompt: {prompt_text}")
        video = RawTextBasedVideo(prompt_text)
        await video.build(build_settings=video_build_settings)
        shutil.move(video.media_url, output_file)
        print(f"video saved on {output_file}")


async def batch_image_based_prompting(prompt_file: str, output_path: str):

    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)
    for _, row in prompt_df.iterrows():
        prompt_path = row.iloc[1]
        output_file = f"./{output_path}{row.iloc[0]}.mp4"

        video, build_settings = await generate_single_image_based_video(prompt_path)
        await video.build(build_settings=build_settings)

        assert video.media_url, "media URL was not updated"
        assert os.path.exists(
            video.media_url
        ), f"The generated video {video.media_url} does not exist"
        shutil.move(video.media_url, output_file)
        print(f"video saved on {output_file}")


async def generate_single_image_based_video(
    prompt_content, title="image_prompt", text="test"
):
    build_settings = VideoBuildSettings(
        music_building_context=MusicBuildingContext(
            apply_background_music=False,
            generate_background_music=False,
        ),
        test_mode=False,
        target_model_provider="stabilityai_image",
    )
    image_prompt = PromptFactory(
        ml_gateway=build_settings.get_ml_models_gateway()
    ).create_prompt_from_image(image_path=prompt_content, text="image prompt")
    image_prompt._text = text

    video = RawImageBasedVideo(
        raw_image_prompt=image_prompt._image,
        title=title,
    )
    video.build_settings = build_settings
    build_settings.prompt = image_prompt
    return video, build_settings


async def batch_composed_prompting(prompt_file: str, output_path: str):

    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)
    # at least 2 prompts
    assert len(prompt_df) > 1, "You need at least 2 prompts"
    vid_cp_sub = CompositeVideo()

    text_based_video_build_settings = VideoBuildSettings(
        music_building_context=MusicBuildingContext(
            apply_background_music=False, generate_background_music=False
        ),
        interpolate=False,
        test_mode=False,
        target_model_provider="stabilityai",
    )

    for i in range(0, len(prompt_df) - 1, 2):
        first_prompt_type = prompt_df.iloc[i]["type"]
        first_prompt_content = prompt_df.iloc[i]["prompt"]

        second_prompt_type = prompt_df.iloc[i + 1]["type"]
        second_prompt_content = prompt_df.iloc[i + 1]["prompt"]

        if first_prompt_type == "image":
            first_video, image_based_video_build_settings = (
                await generate_single_image_based_video(
                    first_prompt_content,
                    title=prompt_df.iloc[i]["name"],
                    text=f"video {i}",
                )
            )
            first_video.build_settings = image_based_video_build_settings

        elif first_prompt_type == "text":
            first_video = RawTextBasedVideo(first_prompt_content)
            first_video.build_settings = text_based_video_build_settings

        await first_video.prepare_build(build_settings=first_video.build_settings)

        if second_prompt_type == "image":
            second_video, image_based_video_build_settings = (
                await generate_single_image_based_video(
                    second_prompt_content,
                    title=prompt_df.iloc[i + 1]["name"],
                    text=f"video {i+1}",
                )
            )
            second_video.build_settings = image_based_video_build_settings

        elif second_prompt_type == "text":
            second_video = RawTextBasedVideo(second_prompt_content)
            second_video.build_settings = text_based_video_build_settings

        await second_video.prepare_build(build_settings=second_video.build_settings)

        vid_cp_sub.append_video(first_video).append_video(second_video)
    await vid_cp_sub.build(build_settings=VideoBuildSettings())
    shutil.move(vid_cp_sub.media_url, "composite.mp4")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--prompt_file",
        default="inputs/Drama/input.csv",
        type=str,
        help="The path to the CSV file containing prompts.",
    )
    parser.add_argument(
        "--output_path",
        default="inputs/Drama/",
        type=str,
        help="The path to the folder to save videos.",
    )

    parser.add_argument(
        "--model_provider",
        default="stabilityai",
        type=str,
        help="chose the model provider: stabilityai, videocrafter, haiper, stabilityai_image",
    )

    # Parse the command-line arguments
    args = parser.parse_args()
    # asyncio.run(
    #     batch_raw_text_based_prompting(
    #         args.prompt_file, args.output_path, args.model_provider
    #     )
    # )

    # asyncio.run(
    #     batch_image_based_prompting(
    #         "inputs/image_based/input.csv", "inputs/image_based/"
    #     )
    # )

    with WorkingFolderContext("./working_directory/"):
        asyncio.run(
            batch_composed_prompting("inputs/composed/input.csv", "inputs/composed/")
        )
