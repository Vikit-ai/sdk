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
from vikit.video.raw_multimodal_based_video import RawMultiModalBasedVideo
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
        "runway": 5.0,
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

    prompt = await PromptFactory().create_prompt_from_text(prompt)

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
            target_model_provider="haiper", #Available models: videocrafter, stabilityai, haiper
            output_video_file_name="AICosmetics.mp4",
            interpolate=True,
            aspect_ratio=(9,16),
        )

        prompt = "Unlock your radiance with AI Cosmetics."  # @param {type:"string"}
        ml_models_gateway = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=False)
        prompt = await PromptFactory(ml_models_gateway=ml_models_gateway).create_prompt_from_multimodal_async(text=prompt, negative_text="human faces", duration=2)
        video = RawMultiModalBasedVideo(prompt=prompt)
        await video.build(build_settings=video_build_settings, ml_models_gateway=ml_models_gateway)

async def is_qualitative_until(media_url, ml_models_gateway, gemini_version="gemini-1.5-pro-002"):

    prompt_is_outdoor = await PromptFactory().create_prompt_from_multimodal_async(text="""
You are an part of a program that will determine if a video should be processed further.

If the scene showcases an human, output True.

If theere is no human, output False.

Output ONLY True or False nothing else. No other text or characters are allowed. Do not get wrong. Do not output any text.

    """,  video=media_url)
    is_outdoor = await ml_models_gateway.ask_gemini(prompt_is_outdoor, gemini_version)

    if ("True" in is_outdoor): 
        print("Outside")

        prompt_ouside = await PromptFactory().create_prompt_from_multimodal_async(text="""
You are an part of a program that will determine if a video will be trimmed if yes you will output the second and if not -1. Perform a frame-by-frame analysis of the provided video. 

Identify if there is an human face and if this human face looks blurry, or weird.

If nothing of this happens, respond with -1. Output ONLY the second or -1 nothing else. No other text or characters are allowed. Do not get wrong. Do not output any text.
        """,  video=media_url)
        response = await ml_models_gateway.ask_gemini(prompt_ouside, gemini_version)
        return str(response)
    else:
        return -1

async def quality_check_with_gemini():
    working_folder="./examples/inputs/ImageOnly/"
    with WorkingFolderContext(working_folder):
        gemini_prompt="""
            **Instruction:**  You are a prompt generator specializing in creating text prompts for Runway Gen-3 Alpha, an AI video generation model.  Given an input image and a desired camera movement, you will output a concise and effective prompt that achieves the desired effect.  The prompt should adhere to Runway's best practices for optimal results.

            **Input Image:** [Insert Image Here]

            **Desired Camera Movement:** Analyze the provided image and determine the most effective camera movement to transform it into a compelling real estate video.  Choose from the following options: slowly zoom in. The camera movement must be smooth and stable, and no elements should be added to the image.  The goal is to showcase the space in the most appealing way. If there is a window somewhere, the zoom should go in the other direction.

            **Output:** A single, concise text prompt designed for Runway Gen-3 Alpha that will animate the input image using the chosen camera movement.  The prompt should be less than 20 words if possible, and prioritize clarity and precision. Do not include any explanation or commentary, only the prompt itself.
            """

        ml_models_gateway = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=False)

        video_build_settings = VideoBuildSettings(
            output_video_file_name="image.mp4",
            target_model_provider="haiper",
        )

        vid_cp_final = CompositeVideo()
        vid_cp_final._is_root_video_composite = True
        for i in range(1, 2):
            current_image = str(i) + ".jpg"
            prompt = await PromptFactory().create_prompt_from_multimodal_async(text=gemini_prompt,  image=current_image, reengineer_text_prompt_from_image_and_text=True)

            # Query Gemini to get an appropriate prompt
            response = await ml_models_gateway.ask_gemini(prompt)
            
            #Then we create an image based video for the last video, for example to showcase a product
            image_prompt = await PromptFactory(ml_models_gateway=ml_models_gateway).create_prompt_from_image(
                    image=current_image,
                    text=response.strip() + ". Slow motion.",
                    model_provider="haiper",
                    duration=2,
                )

            image_based_video = RawImageBasedVideo(prompt=image_prompt)
            vid_cp_final.append_video(image_based_video)
        
        await vid_cp_final.build(ml_models_gateway=ml_models_gateway, build_settings=video_build_settings, quality_check=is_qualitative_until)
        print(f"Saved video {vid_cp_final.media_url}")



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
            prompt = """Paris, the City of Light """ #is a global center of art, fashion, and culture, renowned for its iconic landmarks and romantic atmosphere. The Eiffel Tower, Louvre Museum, and Notre-Dame Cathedral are just a few of the city's must-see attractions. Paris is also famous for its charming cafes, chic boutiques, and world-class cuisine, offering visitors a delightful blend of history, elegance, and joie de vivre along the scenic Seine River."""
            asyncio.run(prompt_based_composite(prompt=prompt, model_provider="haiper"))
    
    elif run_an_example == 7:
        asyncio.run(colabCode())
    elif run_an_example == 8:
        asyncio.run(quality_check_with_gemini())
