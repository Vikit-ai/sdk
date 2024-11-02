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

import argparse
import asyncio
import os

import pandas as pd  # type: ignore
from loguru import logger  # type: ignore

from vikit.common.context_managers import WorkingFolderContext
from vikit.common.decorators import log_function_params
from vikit.music_building_context import MusicBuildingContext
from vikit.prompt.prompt_factory import PromptFactory
from vikit.video.composite_video import CompositeVideo
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.video.raw_image_based_video import RawImageBasedVideo
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.seine_transition import SeineTransition
from vikit.video.transition import Transition
from vikit.video.video import VideoBuildSettings
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory

negative_prompt = """bad anatomy, bad hands, missing fingers, extra fingers, three hands, 
three legs, bad arms, missing legs, missing arms, poorly drawn face, bad face, fused face, 
cloned face, three crus, fused feet, fused thigh, extra crus, ugly fingers, amputation,
 disconnected limbs"""


@log_function_params
def get_estimated_duration(composite: CompositeVideo) -> float:
    """Get an estimation of a composite video's duration, based on the type of the sub-videos"""
    duration_dict = {
        "": 4.04,
        "vikit": 4.04,
        "stabilityai": 4.04,
        "stabilityai_image": 4.04,
        "videocrafter": 2.0,
        "dynamicrafter": 2.0,
        "haiper": 4.0,
        "transition": 2.0,
        "runway": 10.0,
    }
    duration = 0
    for video in composite.video_list:
        interpolation_factor = 1.9 if video.build_settings.interpolate else 1.0
        if isinstance(video, Transition):
            duration += duration_dict["transition"] * interpolation_factor
        else:
            duration += (
                duration_dict[video.build_settings.target_model_provider]
                * interpolation_factor
            )
    return duration


async def batch_raw_text_based_prompting(
    prompt_file: str, model_provider: str = "stabilityai"
):
    # It is strongly recommended to activate interpolate for videocrafter model
    to_interpolate = True if model_provider == "videocrafter" else False
    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)

    for _, row in prompt_df.iterrows():
        output_file = f"{row.iloc[0]}.mp4"
        prompt_content = row.iloc[1]

        video_build_settings = VideoBuildSettings(
            music_building_context=MusicBuildingContext(
                apply_background_music=True,
                generate_background_music=True,
                expected_music_length=5,
            ),
            interpolate=to_interpolate,
            target_model_provider=model_provider,
            output_video_file_name=output_file,
        )

        prompt_obj = await PromptFactory().create_prompt_from_text(prompt_content)

        # you can set negative prompt, for the moment it is  effective only for Haiper
        prompt_obj.negative_prompt = negative_prompt
        video_build_settings.prompt = prompt_obj

        video = RawTextBasedVideo(prompt_content)
        await video.build(build_settings=video_build_settings)


async def composite_textonly_prompting(
    prompt_file: str, model_provider: str = "stabilityai"
):

    # It is strongly recommended to activate interpolate for videocrafter model
    to_interpolate = True if model_provider == "videocrafter" else False

    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)

    vid_cp_sub = CompositeVideo()
    subtitle_total = ""

    for i in range(len(prompt_df)):
        prompt_content = prompt_df.iloc[i]["prompt"]
        subtitle_total += prompt_content

        video = RawTextBasedVideo(prompt_content)

        video.build_settings = VideoBuildSettings(
            interpolate=to_interpolate,
            target_model_provider=model_provider,
        )
        # add transitions from time to time
        if i >= 1 and i % 2 == 0:
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
            expected_music_length=total_duration * 1.5,
        ),
        target_model_provider=model_provider,
        output_video_file_name="Composite.mp4",
        expected_length=total_duration,
        include_read_aloud_prompt=True,
    )
    prompt = await PromptFactory().create_prompt_from_text(subtitle_total)
    # you can set negative prompt, for the moment it is  effective only for Haiper
    prompt.negative_prompt = negative_prompt
    composite_build_settings.prompt = prompt

    await vid_cp_sub.build(build_settings=composite_build_settings)


async def create_single_image_based_video(
    prompt_content,
    build_settings=None,
    output_filename: str = None,
    text: str = None,
):
    """text: would be basically used for music generation, if applicable"""
    if build_settings is None:
        build_settings = VideoBuildSettings(
            target_model_provider="stabilityai_image",
            output_video_file_name=output_filename,
        )
    image_prompt = PromptFactory().create_prompt_from_image(image=prompt_content, text=text)

    video = RawImageBasedVideo(
        prompt=image_prompt,
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
                expected_music_length=5,
            ),
            target_model_provider="stabilityai_image",
            output_video_file_name=output_file,
            expected_length=4,
        )

        video, _ = await create_single_image_based_video(
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

    model_provider = "videocrafter"

    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)

    single_video_buildsettings = VideoBuildSettings(
        target_model_provider=model_provider,
    )

    vid_cp_sub = CompositeVideo()

    for i in range(len(prompt_df)):
        prompt_content = prompt_df.iloc[i]["prompt"]

        video, _ = await create_single_image_based_video(
            prompt_content=prompt_content,
            build_settings=single_video_buildsettings,
            text="Moving fast"
        )
        # Add transitions from time to time
        if i >= 1 and i % 2 == 0:
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
            expected_music_length=total_duration * 1.5,
        ),
        target_model_provider=model_provider,
        output_video_file_name="Composite.mp4",
        expected_length=total_duration,
    )
    # The text is used to generate music, if applicable
    composite_build_settings.prompt = await PromptFactory().create_prompt_from_text(
        "A happy picnic music!"
    )
    await vid_cp_sub.build(build_settings=composite_build_settings)


async def composite_mixed_prompting(
    prompt_file: str, text_to_video_model_provider: str = "stabilityai"
):

    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)

    # It is strongly recommended to activate interpolate for videocrafter model
    to_interpolate = True if text_to_video_model_provider == "videocrafter" else False

    text_based_video_buildsettings = VideoBuildSettings(
        target_model_provider=text_to_video_model_provider,
        interpolate=to_interpolate,
    )

    vid_cp_sub = CompositeVideo()

    for i in range(len(prompt_df)):

        prompt_content = prompt_df.iloc[i]["prompt"]
        prompt_type = prompt_df.iloc[i]["type"]

        if prompt_type == "image":
            image_based_video_buildsettings = VideoBuildSettings(
                target_model_provider="stabilityai_image",
            )
            video, image_based_video_buildsettings = (
                await create_single_image_based_video(
                    prompt_content=prompt_content,
                    build_settings=image_based_video_buildsettings,
                    text="Moving fast"
                )
            )

        elif prompt_type == "text":
            video = RawTextBasedVideo(prompt_content)
            video.build_settings = text_based_video_buildsettings

        else:
            logger.debug(f"Error! prompt type {prompt_type} not recognized!")
            continue

        await video.prepare_build(build_settings=video.build_settings)

        # Add transitions from time to time
        if i >= 1 and i % 2 == 0:
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
            expected_music_length=total_duration * 1.5,
        ),
        output_video_file_name="Composite.mp4",
        expected_length=total_duration,
    )

    composite_build_settings.prompt = await PromptFactory().create_prompt_from_text(
        "A happy Guitar music!"
    )
    await vid_cp_sub.build(build_settings=composite_build_settings)


async def prompt_based_composite(prompt: str, model_provider="stabilityai"):

    # It is strongly recommended to activate interpolate for videocrafter model
    to_interpolate = True if model_provider == "videocrafter" else False

    video_build_settings = VideoBuildSettings(
        music_building_context=MusicBuildingContext(
            apply_background_music=True,
            generate_background_music=True,
        ),
        include_read_aloud_prompt=True,
        target_model_provider=model_provider,
        output_video_file_name="Composite.mp4",
        interpolate=to_interpolate,
    )

    gw = video_build_settings.get_ml_models_gateway()
    prompt = await PromptFactory(ml_models_gateway=gw).create_prompt_from_text(prompt)
    # you can set negative prompt, for the moment it is  effective only for Haiper
    prompt.negative_prompt = negative_prompt
    video = PromptBasedVideo(prompt=prompt)
    await video.build(build_settings=video_build_settings)


async def colabCode():
    working_folder="./examples/inputs/PromptbasedVideo/"
    with WorkingFolderContext(working_folder):
        video_build_settings = VideoBuildSettings(
            music_building_context=MusicBuildingContext(
                apply_background_music=True,
                generate_background_music=True,
            ),
            include_read_aloud_prompt=True,
            target_model_provider="runway", #Available models: videocrafter, stabilityai, haiper
            output_video_file_name="AICosmetics.mp4",
            interpolate=True,
        )

        prompt = "Unlock your radiance with AI Cosmetics."  # @param {type:"string"}

        prompt = await PromptFactory().create_prompt_from_text(prompt)
        video = PromptBasedVideo(prompt=prompt)
        await video.build(build_settings=video_build_settings)

async def call_gemini():
    working_folder="./examples/inputs/PromptbasedVideo/"
    with WorkingFolderContext(working_folder):

        
        prompt = await PromptFactory().create_prompt_from_multimodal_async(text="Is the camera revealing more of the scene not present at the begining, or showing blurry things ? If it does, respond True else False. Just respond True or False nothing else. Do not get wrong. Most of the time, camera zooming in is True and else False. Explain you answer.",  video="https://dnznrvs05pmza.cloudfront.net/ec689c70-2572-4d63-bb41-6c797c77259a.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiNzYyMGI3Y2MxZjczZjA5ZCIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMDUwNTYwMH0.RMpLWTkTVS_6RJDv8tved2oahTOt8CtgIMt9GCl6gJ4")
        gateway = MLModelsGatewayFactory().get_ml_models_gateway()
        print(await gateway.ask_gemini(prompt))



if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--example",
        default=None,
        type=int,
        help="choose one of the predefined examples to run",
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    run_an_example = args.example
    if run_an_example is None:
        pass
    elif run_an_example == 1:
        # Example 1- Create a composite of text-based videos:
        with WorkingFolderContext("./examples/inputs/TextOnlyComposite"):
            logger.add("log.txt")
            asyncio.run(composite_textonly_prompting("./input.csv"))

    elif run_an_example == 2:
        # Example 2- Create a batch of text-based videos:
        with WorkingFolderContext("./examples/inputs/TextOnly"):
            logger.add("log.txt")
            asyncio.run(
                batch_raw_text_based_prompting("./input.csv", model_provider="haiper")
            )

    elif run_an_example == 3:
        # Example 3 - Create a batch of videos from images
        with WorkingFolderContext("./examples/inputs/ImageOnly/"):
            logger.add("log.txt")
            asyncio.run(
                batch_image_based_prompting(
                    "input.csv",
                )
            )
    elif run_an_example == 4:
        # Example 4 - Create a composite of image-based videos:
        with WorkingFolderContext("./examples/inputs/ImageOnlyComposite/"):
            logger.add("log.txt")
            asyncio.run(
                composite_imageonly_prompting(
                    "input.csv",
                )
            )

    elif run_an_example == 5:
        # Example 5 - Create a composite of text and image-based videos:
        with WorkingFolderContext("./examples/inputs/Mixed/"):
            logger.add("log.txt")
            asyncio.run(
                composite_mixed_prompting(
                    "input.csv",
                )
            )
    elif run_an_example == 6:
        # Example 6 - Create a prompt-based videos
        with WorkingFolderContext("./examples/inputs/PromptBased/"):
            logger.add("log.txt")
            prompt = """Paris, the City of Light, is a global center of art, fashion, and culture, renowned for its iconic landmarks and romantic atmosphere. The Eiffel Tower, Louvre Museum, and Notre-Dame Cathedral are just a few of the city's must-see attractions. Paris is also famous for its charming cafes, chic boutiques, and world-class cuisine, offering visitors a delightful blend of history, elegance, and joie de vivre along the scenic Seine River."""
            asyncio.run(prompt_based_composite(prompt=prompt))
    
    elif run_an_example == 7:
        asyncio.run(colabCode())
    elif run_an_example == 8:
        asyncio.run(call_gemini())
