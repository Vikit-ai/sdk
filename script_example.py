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
from vikit.video.transition import Transition
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
import asyncio
from vikit.prompt.prompt_factory import PromptFactory
from vikit.video.raw_image_based_video import RawImageBasedVideo
from vikit.video.video import VideoBuildSettings
from vikit.common.context_managers import WorkingFolderContext
from vikit.music_building_context import MusicBuildingContext


async def batch_raw_text_based_prompting(
    prompt_file: str, model_provider: str = "videocrafter"
):
    to_interpolate = True if model_provider == "videocrafter" else False

    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)
    for _, row in prompt_df.iterrows():
        output_file = f"{row.iloc[0]}.mp4"
        prompt = await PromptFactory().create_prompt_from_text(row.iloc[1])
        video_build_settings = VideoBuildSettings(
            music_building_context=MusicBuildingContext(
                apply_background_music=True, generate_background_music=True
            ),
            test_mode=False,
            interpolate=to_interpolate,
            target_model_provider=model_provider,
            output_video_file_name=output_file,
        )
        video_build_settings.prompt = prompt
        video = RawTextBasedVideo(prompt.text)
        await video.build(build_settings=video_build_settings)


def get_estimated_duration(composite: CompositeVideo):
    """Get an estimation of a composite video's duration, based on the type of the sub-videos"""
    duration_dict = {
        "": 3.9,
        "vikit": 3.9,
        "stabilityai": 3.9,
        "stabilityai_image": 3.9,
        "seine": 4.0,
        "videocrafter": 2.0,
        "haiper": 3.9,
    }
    duration = 0
    for video in composite.video_list:
        if isinstance(video, Transition):
            duration += 2.0
        else:
            duration += duration_dict[video.build_settings.target_model_provider]
    return duration


async def composite_textonly_prompting(prompt_file: str):

    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)
    # At least 2 prompts
    assert len(prompt_df) > 1, "You need at least 2 prompts"
    vid_cp_sub = CompositeVideo()
    single_video_buildsettings = VideoBuildSettings(
        interpolate=False,
        test_mode=False,
        target_model_provider="videocrafter",
    )

    for i in range(len(prompt_df)):
        prompt_content = prompt_df.iloc[i]["prompt"]
        video = RawTextBasedVideo(prompt_content)
        video.build_settings = single_video_buildsettings
        if i >= 1:
            transition_video = SeineTransition(
                source_video=vid_cp_sub.video_list[i - 1],
                target_video=video,
            )
            vid_cp_sub.append_video(transition_video)
        vid_cp_sub.append_video(video)

    total_duration = get_estimated_duration(vid_cp_sub)
    composite_build_settings = VideoBuildSettings(
        music_building_context=MusicBuildingContext(
            apply_background_music=True,
            generate_background_music=True,
            expected_music_length=total_duration,
        ),
        interpolate=False,
        test_mode=False,
        target_model_provider="videocrafter",
        output_video_file_name="Composit.mp4",
        expected_length=total_duration,
    )
    # set up music prompt
    composite_build_settings.prompt = await PromptFactory().create_prompt_from_text(
        " A cool music"
    )
    await vid_cp_sub.build(build_settings=composite_build_settings)


async def generate_single_image_based_video(
    prompt_content,
    build_settings=None,
    test_mode=True,
    output_filename: str = None,
    text: str = None,
):
    """text: would be basically used for music generation, if applicable"""
    if build_settings is None:
        build_settings = VideoBuildSettings(
            test_mode=test_mode,
            target_model_provider="stabilityai_image",
            output_video_file_name=output_filename,
        )
    image_prompt = PromptFactory(
        ml_gateway=build_settings.get_ml_models_gateway()
    ).create_prompt_from_image(image_path=prompt_content, text=text)

    video = RawImageBasedVideo(
        raw_image_prompt=image_prompt._image,
    )
    video.build_settings = build_settings
    build_settings.prompt = image_prompt
    return video, build_settings


async def batch_image_based_prompting(prompt_file: str):

    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)
    for _, row in prompt_df.iterrows():
        prompt_path = row.iloc[1]
        output_file = f"{row.iloc[0]}.mp4"

        build_settings = VideoBuildSettings(
            music_building_context=MusicBuildingContext(
                apply_background_music=True,
                generate_background_music=True,
                expected_music_length=4,
            ),
            test_mode=False,
            interpolate=False,
            target_model_provider="stabilityai_image",
            output_video_file_name=output_file,
            expected_length=4,
        )

        video, _ = await generate_single_image_based_video(
            prompt_content=prompt_path,
            text="A cool music for picnic",
            build_settings=build_settings,
        )
        await video.build(build_settings=build_settings)

        assert video.media_url, "media URL was not updated"
        assert os.path.exists(
            video.media_url
        ), f"The generated video {video.media_url} does not exist"
        print(f"video saved on {output_file}")


async def composite_imageonly_prompting(prompt_file: str):

    TEST_MODE = False
    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)
    # at least 2 prompts
    assert len(prompt_df) > 1, "You need at least 2 prompts"

    single_video_buildsettings = VideoBuildSettings(
        interpolate=False,
        test_mode=TEST_MODE,
        target_model_provider="stabilityai_image",
    )

    vid_cp_sub = CompositeVideo()

    for i in range(len(prompt_df)):
        prompt_content = prompt_df.iloc[i]["prompt"]
        video, _ = await generate_single_image_based_video(
            prompt_content=prompt_content,
            build_settings=single_video_buildsettings,
        )
        if i >= 1:
            transition_video = SeineTransition(
                source_video=vid_cp_sub.video_list[i - 1],
                target_video=video,
            )
            vid_cp_sub.append_video(transition_video)
        vid_cp_sub.append_video(video)

    total_duration = get_estimated_duration(vid_cp_sub)
    composite_build_settings = VideoBuildSettings(
        music_building_context=MusicBuildingContext(
            apply_background_music=True,
            generate_background_music=True,
            expected_music_length=total_duration,
        ),
        test_mode=TEST_MODE,
        target_model_provider="stabilityai_image",
        output_video_file_name="Composit.mp4",
        expected_length=total_duration,
    )
    composite_build_settings.prompt = await PromptFactory().create_prompt_from_text(
        "A happy picnic music!"
    )
    await vid_cp_sub.build(build_settings=composite_build_settings)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--prompt_file",
        default="inputs/TextOnly/input.csv",
        type=str,
        help="The path to the CSV file containing prompts.",
    )
    parser.add_argument(
        "--output_path",
        default="inputs/TextOnly/",
        type=str,
        help="The path to the folder to save videos.",
    )

    parser.add_argument(
        "--model_provider",
        default="videocrafter",
        type=str,
        help="chose the model provider: stabilityai, videocrafter, haiper, stabilityai_image",
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # # Example 1- Create a composite of text-based videos:
    # with WorkingFolderContext("./examples/inputs/TextOnly"):
    #     logger.add("log.txt")
    #     asyncio.run(composite_textonly_prompting("./input.csv"))

    # # Example 2- Create a batch of text-based videos:
    # with WorkingFolderContext("./examples/inputs/TextOnly"):
    #     logger.add("log.txt")
    #     asyncio.run(batch_raw_text_based_prompting("./input.csv"))

    # # Example 3 - Create a batch of videos from images
    # with WorkingFolderContext("./examples/inputs/ImageOnly/"):
    #     logger.add("log.txt")
    #     asyncio.run(
    #         batch_image_based_prompting(
    #             "input.csv",
    #         )
    #     )

    # Example 4 - Create a batch of videos from images
    with WorkingFolderContext("./examples/inputs/ImageOnly/"):
        logger.add("log.txt")
        asyncio.run(
            composite_imageonly_prompting(
                "input.csv",
            )
        )
