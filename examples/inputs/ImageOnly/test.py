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
from vikit.common.decorators import log_function_params
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.video.transition import Transition
from vikit.video.composite_video import CompositeVideo
from vikit.video.seine_transition import SeineTransition
from vikit.video.video import VideoBuildSettings
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.raw_image_based_video import RawImageBasedVideo
from vikit.music_building_context import MusicBuildingContext
from loguru import logger  # type: ignore
import pandas as pd  # type: ignore
import argparse
import asyncio
from vikit.prompt.prompt_factory import PromptFactory
from vikit.common.context_managers import WorkingFolderContext


@log_function_params
def get_estimated_duration(composite: CompositeVideo):
    """Get an estimation of a composite video's duration, based on the type of the sub-videos"""
    duration_dict = {
        "": 3.9,
        "vikit": 3.9,
        "stabilityai": 3.9,
        "stabilityai_image": 3.9,
        "videocrafter": 2.0,
        "haiper": 3.9,
    }
    duration = 0
    for video in composite.video_list:
        if video.build_settings.interpolate:
            interpolation_factor = 2.0
        else:
            interpolation_factor = 1.0
        if isinstance(video, Transition):
            duration += 2.0 * interpolation_factor
        else:
            duration += (
                duration_dict[video.build_settings.target_model_provider]
                * interpolation_factor
            )
    return duration


async def batch_raw_text_based_prompting(
    prompt_file: str, model_provider: str = "videocrafter"
):
    to_interpolate = True if model_provider == "videocrafter" else False

    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)
    for _, row in prompt_df.iterrows():
        output_file = f"{row.iloc[0]}.mp4"
        video_build_settings = VideoBuildSettings(
            music_building_context=MusicBuildingContext(
                apply_background_music=True, generate_background_music=True
            ),
            test_mode=False,
            interpolate=to_interpolate,
            target_model_provider=model_provider,
            output_video_file_name=output_file,
        )
        prompt = await PromptFactory(
            ml_gateway=video_build_settings.get_ml_models_gateway()
        ).create_prompt_from_text(row.iloc[1])
        video_build_settings.prompt = prompt
        video = RawTextBasedVideo(prompt.text)
        await video.build(build_settings=video_build_settings)


async def composite_textonly_prompting(prompt_file: str):
    TEST_MODE = False
    model_provider = "videocrafter"
    to_interpolate = True if model_provider == "videocrafter" else False
    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)
    # At least 2 prompts
    assert len(prompt_df) > 1, "You need at least 2 prompts"
    vid_cp_sub = CompositeVideo()
    single_video_buildsettings = VideoBuildSettings(
        interpolate=to_interpolate,
        test_mode=TEST_MODE,
        target_model_provider=model_provider,
    )
    for i in range(len(prompt_df)):
        prompt_content = prompt_df.iloc[i]["prompt"]
        video = RawTextBasedVideo(prompt_content)
        video.build_settings = single_video_buildsettings
        if i >= 1:
            n_videos = len(vid_cp_sub.video_list)
            transition_video = SeineTransition(
                source_video=vid_cp_sub.video_list[n_videos - 1],
                target_video=video,
            )
            vid_cp_sub.append_video(transition_video)
        # Here we prepare the video before asking to build and using a tailored made build-settings
        await video.prepare_build(build_settings=video.build_settings)
        vid_cp_sub.append_video(video)

    # Here we decide to set music only for the global video
    total_duration = get_estimated_duration(vid_cp_sub)
    composite_build_settings = VideoBuildSettings(
        music_building_context=MusicBuildingContext(
            apply_background_music=True,
            generate_background_music=True,
            expected_music_length=total_duration + 1,
        ),
        test_mode=TEST_MODE,
        target_model_provider=model_provider,
        output_video_file_name="Composit.mp4",
        expected_length=total_duration,
    )
    # set up music prompt
    composite_build_settings.prompt = await PromptFactory().create_prompt_from_text(
        " Classic French music!"
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
            n_videos = len(vid_cp_sub.video_list)
            transition_video = SeineTransition(
                source_video=vid_cp_sub.video_list[n_videos - 1],
                target_video=video,
            )
            vid_cp_sub.append_video(transition_video)
        await video.prepare_build(build_settings=video.build_settings)
        vid_cp_sub.append_video(video)

    total_duration = get_estimated_duration(vid_cp_sub)
    composite_build_settings = VideoBuildSettings(
        music_building_context=MusicBuildingContext(
            apply_background_music=True,
            generate_background_music=True,
            expected_music_length=total_duration + 1,
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


async def composite_mixed_prompting(prompt_file: str):

    TEST_MODE = False
    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)
    # at least 2 prompts
    assert len(prompt_df) > 1, "You need at least 2 prompts"

    text_based_video_buildsettings = VideoBuildSettings(
        test_mode=TEST_MODE,
        target_model_provider="videocrafter",
    )

    vid_cp_sub = CompositeVideo()

    for i in range(len(prompt_df)):
        prompt_content = prompt_df.iloc[i]["prompt"]
        prompt_type = prompt_df.iloc[i]["type"]
        if prompt_type == "image":
            image_based_video_buildsettings = VideoBuildSettings(
                test_mode=TEST_MODE,
                target_model_provider="stabilityai_image",
            )
            video, image_based_video_buildsettings = (
                await generate_single_image_based_video(
                    prompt_content=prompt_content,
                    build_settings=image_based_video_buildsettings,
                )
            )

        elif prompt_type == "text":
            video = RawTextBasedVideo(prompt_content)
            video.build_settings = text_based_video_buildsettings
        else:
            logger.debug(f"Error! prompt type {prompt_type} not recognized!")
            continue

        await video.prepare_build(build_settings=video.build_settings)

        if i >= 4:
            n_videos = len(vid_cp_sub.video_list)
            transition_video = SeineTransition(
                source_video=vid_cp_sub.video_list[n_videos - 1],
                target_video=video,
            )
            vid_cp_sub.append_video(transition_video)
        vid_cp_sub.append_video(video)

    total_duration = get_estimated_duration(vid_cp_sub)
    composite_build_settings = VideoBuildSettings(
        music_building_context=MusicBuildingContext(
            apply_background_music=True,
            generate_background_music=True,
            expected_music_length=total_duration + 1,
        ),
        test_mode=TEST_MODE,
        output_video_file_name="Composit.mp4",
        expected_length=total_duration,
    )

    composite_build_settings.prompt = await PromptFactory().create_prompt_from_text(
        "A happy Guitar music!"
    )
    await vid_cp_sub.build(build_settings=composite_build_settings)


async def prompte_based_composite(prompt: str):

    video_build_settings = VideoBuildSettings(
        music_building_context=MusicBuildingContext(
            apply_background_music=True,
            generate_background_music=True,
        ),
        test_mode=False,
        include_read_aloud_prompt=True,
        target_model_provider="videocrafter",
        output_video_file_name="Composite.mp4",
        interpolate=True,
    )

    gw = video_build_settings.get_ml_models_gateway()
    prompt = await PromptFactory(ml_gateway=gw).create_prompt_from_text(prompt)
    video = PromptBasedVideo(prompt=prompt)
    await video.build(build_settings=video_build_settings)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--prompt_file",
        default="examples/inputs/TextOnly/input.csv",
        type=str,
        help="The path to the CSV file containing prompts.",
    )
    parser.add_argument(
        "--output_path",
        default="examples/inputs/TextOnly/",
        type=str,
        help="The path to the folder to save videos.",
    )

    parser.add_argument(
        "--model_provider",
        default="videocrafter",
        type=str,
        help="chose the model provider that will be generate all the scenes (but not the transitions if any): stabilityai, videocrafter, haiper, stabilityai_image",
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
    #     asyncio.run(batch_raw_text_based_prompting("./small_input.csv"))

    # # Example 3 - Create a batch of videos from images
    # with WorkingFolderContext("./examples/inputs/ImageOnly/"):
    #     logger.add("log.txt")
    #     asyncio.run(
    #         batch_image_based_prompting(
    #             "input.csv",
    #         )
    #     )

    # # Example 4 - Create a composite of image-based videos:
    # with WorkingFolderContext("./examples/inputs/ImageOnly/"):
    #     logger.add("log.txt")
    #     asyncio.run(
    #         composite_imageonly_prompting(
    #             "input.csv",
    #         )
    #     )

    # Example 5 - Create a composite of text and image-based videos:
    with WorkingFolderContext("./examples/inputs/Mixed2/"):
        logger.add("log.txt")
        asyncio.run(
            composite_imageonly_prompting(
                "input.csv",
            )
        )

    # Example 6 - Create a prompt-based videos
    #with WorkingFolderContext("./examples/inputs/PromptBased5/"):
    #    logger.add("log.txt")
    #
    #    prompt = """London, a city where history and modernity entwine, stretches along the winding path of the River Thames, its skyline a blend of ancient spires 
    #                and glistening skyscrapers. The iconic Big Ben and the towering London Eye stand sentinel over the bustling streets, where red double-decker buses
    #                  and black cabs weave among the crowds. The city's architectural tapestry unfolds in every direction, from the grandeur of Buckingham Palace to 
    #                  the contemporary elegance of The Shard. Along the riverbanks, the vibrant markets of Borough and Camden offer a symphony of flavors and cultures, 
    #                  while the tranquil greenery of Hyde Park and St. James's Park provides a serene escape. As the sun sets, the city transforms into a dazzling spectacle 
    #                  of lights, with the West End's theaters and the neon signs of Piccadilly Circus illuminating the night, embodying the spirit of a city that never 
    #                  truly sleeps."""

    #    asyncio.run(prompte_based_composite(prompt=prompt))
