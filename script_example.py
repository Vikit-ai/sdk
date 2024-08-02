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
        "": 4.04,
        "vikit": 4.04,
        "stabilityai": 4.04,
        "stabilityai_image": 4.04,
        "videocrafter": 2.0,
        "haiper": 4.0,
        "transition": 2.0,
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
    prompt_file: str, model_provider: str = "haiper"
):

    # It is strongly recommended to activate interpolate for videocrafter model
    to_interpolate = True if model_provider == "videocrafter" else False

    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)
    for _, row in prompt_df.iterrows():
        output_file = f"{row.iloc[0]}.mp4"
        prompt_content = row.iloc[1]
        video_build_settings = VideoBuildSettings(
            music_building_context=MusicBuildingContext(
                apply_background_music=False,
                generate_background_music=False,
                expected_music_length=5,
            ),
            interpolate=to_interpolate,
            target_model_provider=model_provider,
            output_video_file_name=output_file,
            test_mode=False,
        )
        video_build_settings.prompt = await PromptFactory(
            ml_gateway=video_build_settings.get_ml_models_gateway()
        ).create_prompt_from_text(prompt_content)

        video = RawTextBasedVideo(prompt_content)
        await video.build(build_settings=video_build_settings)


async def composite_textonly_prompting(prompt_file: str):
    TEST_MODE = True
    # It is strongly recommended to activate interpolate for videocrafter model
    model_provider = "videocrafter"
    to_interpolate = True if model_provider == "videocrafter" else False
    prompt_df = pd.read_csv(prompt_file, delimiter=";", header=0)
    # At least 2 prompts
    assert len(prompt_df) > 1, "You need at least 2 prompts"
    vid_cp_sub = CompositeVideo()

    for i in range(len(prompt_df)):
        prompt_content = prompt_df.iloc[i]["prompt"]
        video = RawTextBasedVideo(prompt_content)
        video.build_settings = VideoBuildSettings(
            interpolate=to_interpolate,
            test_mode=TEST_MODE,
            target_model_provider=model_provider,
            include_read_aloud_prompt=True,
        )
        prompt = await PromptFactory(
            ml_gateway=video.build_settings.get_ml_models_gateway()
        ).create_prompt_from_text(prompt_content)
        video.build_settings.prompt = prompt
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
            generate_background_music=False,
            expected_music_length=total_duration * 1.5,
        ),
        test_mode=TEST_MODE,
        target_model_provider=model_provider,
        output_video_file_name="Composite.mp4",
        expected_length=total_duration,
        include_read_aloud_prompt=True,
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
                apply_background_music=False,
                generate_background_music=False,
                expected_music_length=5,
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
            apply_background_music=False,
            generate_background_music=False,
            expected_music_length=total_duration * 1.5,
        ),
        test_mode=TEST_MODE,
        target_model_provider="stabilityai_image",
        output_video_file_name="Composite.mp4",
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
    text_to_video_model_provider = "stabilityai"
    # It is strongly recommended to activate interpolate for videocrafter model
    to_interpolate = True if text_to_video_model_provider == "videocrafter" else False

    text_based_video_buildsettings = VideoBuildSettings(
        test_mode=TEST_MODE,
        target_model_provider=text_to_video_model_provider,
        interpolate=to_interpolate,
        include_read_aloud_prompt=True,
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
            generate_background_music=False,
            expected_music_length=total_duration * 1.2,
        ),
        test_mode=TEST_MODE,
        output_video_file_name="Composite.mp4",
        expected_length=total_duration,
    )

    composite_build_settings.prompt = await PromptFactory().create_prompt_from_text(
        "A happy Guitar music!"
    )
    await vid_cp_sub.build(build_settings=composite_build_settings)


async def prompte_based_composite(prompt: str):

    # It is strongly recommended to activate interpolate for videocrafter model
    model_provider = "videocrafter"
    to_interpolate = True if model_provider == "videocrafter" else False

    video_build_settings = VideoBuildSettings(
        music_building_context=MusicBuildingContext(
            apply_background_music=True,
            generate_background_music=True,
        ),
        test_mode=False,
        include_read_aloud_prompt=True,
        target_model_provider=model_provider,
        output_video_file_name="Composite.mp4",
        interpolate=to_interpolate,
    )

    gw = video_build_settings.get_ml_models_gateway()
    prompt = await PromptFactory(ml_gateway=gw).create_prompt_from_text(prompt)
    video = PromptBasedVideo(prompt=prompt)
    await video.build(build_settings=video_build_settings)


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
        help="chose the model provider that will be generate all the scenes (but not the transitions if any): stabilityai, videocrafter, haiper, stabilityai_image",
    )

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
        with WorkingFolderContext("./examples/inputs/TextOnly_Obama"):
            logger.add("log.txt")
            asyncio.run(composite_textonly_prompting("./input.csv"))

    elif run_an_example == 2:
        # Example 2- Create a batch of text-based videos:
        with WorkingFolderContext("./examples/inputs/TextOnly"):
            logger.add("log.txt")
            asyncio.run(batch_raw_text_based_prompting("./small_input.csv"))

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
        with WorkingFolderContext("./examples/inputs/ImageOnly/"):
            logger.add("log.txt")
            asyncio.run(
                composite_imageonly_prompting(
                    "input.csv",
                )
            )

    elif run_an_example == 5:
        # Example 5 - Create a composite of text and image-based videos:
        with WorkingFolderContext("./examples/inputs/Mixed_Obama/"):
            logger.add("log.txt")
            asyncio.run(
                composite_mixed_prompting(
                    "input.csv",
                )
            )
    elif run_an_example == 6:
        # Example 6 - Create a prompt-based videos
        with WorkingFolderContext("./examples/inputs/PromptBased_Mallorca/"):
            logger.add("log.txt")

            # prompt = """London, a city where history and modernity entwine, stretches along the winding path of the River Thames, its skyline a blend of ancient spires
            #             and glistening skyscrapers. The iconic Big Ben and the towering London Eye stand sentinel over the bustling streets, where red double-decker buses
            #               and black cabs weave among the crowds. The city's architectural tapestry unfolds in every direction, from the grandeur of Buckingham Palace to
            #               the contemporary elegance of The Shard. Along the riverbanks, the vibrant markets of Borough and Camden offer a symphony of flavors and cultures,
            #               while the tranquil greenery of Hyde Park and St. James's Park provides a serene escape. As the sun sets, the city transforms into a dazzling spectacle
            #               of lights, with the West End's theaters and the neon signs of Piccadilly Circus illuminating the night, embodying the spirit of a city that never
            #               truly sleeps."""

            # prompt = """New York City, often referred to as the "City That Never Sleeps," is a vibrant metropolis that pulses with energy and diversity. Its iconic skyline, dominated by towering skyscrapers like the Empire State Building and One World Trade Center, is a testament to its architectural grandeur. The city is a cultural melting pot, where the bustling streets of Times Square meet the serene beauty of Central Park, and where the neon lights of Broadway theaters illuminate the night. From the trendy neighborhoods of Brooklyn to the historic charm of the Statue of Liberty, New York City offers a rich tapestry of experiences that captivate visitors and residents alike."""
            # prompt = """"China, the world's most populous country, is a captivating blend of ancient history and modern innovation. Its vast landscape includes the Himalayas, the Gobi Desert, and the Yangtze River. Iconic landmarks like the Great Wall and the Forbidden City reflect its rich cultural heritage. From bustling cities like Shanghai and Beijing to serene rural villages, China offers diverse experiences. Its renowned cuisine and traditional arts, such as calligraphy and martial arts, showcase the depth of its cultural legacy."""
            # prompt = """Tokyo, the bustling capital of Japan, is a mesmerizing fusion of ancient tradition and futuristic innovation. Its skyline is a breathtaking blend of towering skyscrapers and historic temples, with the iconic Tokyo Tower and Mount Fuji serving as striking backdrops. The city's vibrant districts, such as the neon-lit streets of Shibuya and the trendy boutiques of Harajuku, offer a sensory overload of color and energy. Tokyo is renowned for its exceptional cuisine, from sushi and ramen to high-end dining, earning it the title of the world's most Michelin-starred city. Despite its modernity, Tokyo preserves its cultural heritage through serene gardens, traditional tea ceremonies, and historic sites like the Meiji Shrine, making it a city that seamlessly balances the old and the new."""
            # prompt = """Amsterdam, known as the "Venice of the North," is a charming city crisscrossed by historic canals and lined with iconic architecture from the Dutch Golden Age. It boasts world-class museums like the Rijksmuseum and Van Gogh Museum, and is famous for its bicycle culture and vibrant nightlife. The city's laid-back atmosphere, picturesque canal houses, and rich cultural heritage make it a captivating destination that blends history and modernity seamlessly."""
            # prompt = """Barcelona, the cosmopolitan capital of Spain's Catalonia region, is renowned for its unique architecture, vibrant culture, and Mediterranean charm. The city is synonymous with the whimsical designs of Antoni Gaudí, including the iconic Sagrada Família and the colorful Park Güell. Barcelona's lively streets are filled with tapas bars, bustling markets like La Boqueria, and the energetic promenade of La Rambla. With its sunny beaches, rich history, and passionate embrace of art and cuisine, Barcelona offers an unforgettable blend of tradition and modernity."""
            # prompt = """"Egypt, a land of ancient wonders and timeless beauty, is home to some of the world's most iconic historical sites. The majestic Pyramids of Giza and the enigmatic Sphinx stand as testaments to the country's rich pharaonic heritage. The Nile River, the lifeblood of Egypt, flows through bustling cities like Cairo and Luxor, offering breathtaking views of ancient temples and tombs. From the vibrant markets of Khan El Khalili to the serene beaches of the Red Sea, Egypt is a captivating blend of history, culture, and natural splendor."""
            # prompt = """Argentina, a vast and diverse country in South America, is renowned for its stunning landscapes and vibrant culture. From the bustling streets of Buenos Aires, where tango dancers captivate audiences, to the breathtaking glaciers of Patagonia, Argentina offers a wealth of natural wonders. The country is also famous for its rich gaucho tradition, world-class wine regions like Mendoza, and the awe-inspiring Iguazú Falls. With its passionate embrace of soccer, mouthwatering cuisine, and warm hospitality, Argentina is a destination that truly engages the senses."""
            # prompt = """Greece, the cradle of Western civilization, is a captivating blend of ancient history and stunning natural beauty. Renowned for its iconic landmarks like the Acropolis in Athens and the ancient ruins of Delphi, Greece offers a rich tapestry of archaeological sites that tell the story of its illustrious past. The country is also famous for its picturesque islands, such as Santorini and Mykonos, with their whitewashed villages, crystal-clear waters, and vibrant Mediterranean culture. From its delicious cuisine to its warm hospitality, Greece is a destination that enchants visitors with its timeless charm and cultural heritage."""
            # prompt = """Brazil, the largest country in South America, is a vibrant and diverse land known for its lush rainforests, stunning beaches, and rich cultural heritage. The iconic city of Rio de Janeiro, with its Christ the Redeemer statue and lively Carnival celebrations, embodies the country's energetic spirit. From the vast Amazon rainforest to the bustling metropolis of São Paulo, Brazil offers a captivating blend of natural wonders, colonial architecture, and a passionate love for soccer and samba. Its warm climate, delicious cuisine, and welcoming people make it a destination that truly comes alive with color and rhythm."""
            prompt = """Mallorca, the largest of Spain's Balearic Islands, is a Mediterranean paradise known for its stunning coastline, crystal-clear waters, and picturesque landscapes. The island's capital, Palma, is a vibrant city with a historic cathedral and charming old town. Beyond its beaches, Mallorca offers a rich cultural heritage, with quaint hilltop villages, ancient ruins, and the scenic Serra de Tramuntana mountain range, making it a captivating destination that combines natural beauty with a touch of elegance and tradition."""
            asyncio.run(prompte_based_composite(prompt=prompt))
