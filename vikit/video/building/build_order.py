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

from abc import ABC, abstractmethod

from loguru import logger

from vikit.video.video import Video
from vikit.video.video_build_settings import VideoBuildSettings


class is_composite_video(ABC):
    """
    Interface for composite videos, needed to prevent circular imports
    """

    @abstractmethod
    def is_composite_video(self):
        pass


def get_lazy_dependency_chain_build_order(
    video_tree: list[Video],
    build_settings: VideoBuildSettings,
    already_added: set,
    video_build_order: list[Video] = [],
):
    """
    Get the first videos first build order

    Here we generate the video in a lazy way, starting from the leaf composite and
    going up to the root composite as dependency resolution is done

    So this is a width traversal of the video tree, but we go down the dependency chain too

    params:
        video_tree (list): The video tree to recurse on to parse the tree and get the build order
        build_settings: The build settings
        already_added (set): The set of already added videos

    Returns:
        list: The build order
    """
    logger.trace(f"video_tree len is {len(video_tree)}")
    if len(video_tree) == 1:
        logger.debug(
            f"video_tree single object is  {video_tree[0].id} and type is {type(video_tree[0])}"
        )

    for video in video_tree:
        logger.trace(f"type(video) is {type(video)}")
        if isinstance(video, is_composite_video) and len(video.video_list) > 0:
            logger.trace(f"Going down the dependency chain for {video.id}")
            get_lazy_dependency_chain_build_order(
                video_build_order=video_build_order,
                video_tree=video.video_list,
                build_settings=build_settings,
                already_added=already_added,
            )
        else:  # on a leaf, we need to check if the video has dependencies
            if len(video.video_dependencies) > 0:
                logger.trace(f"On a leaf, going up the dependency chain for {video.id}")
                get_lazy_dependency_chain_build_order(
                    video_build_order=video_build_order,
                    video_tree=video.video_dependencies,
                    build_settings=build_settings,
                    already_added=already_added,
                )
        if video.id not in already_added:
            logger.trace(f"Adding video {video.id} to the build order")
            video_build_order.append(video)
            already_added.add(video.id)

    return video_build_order
