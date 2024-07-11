from abc import abstractmethod, ABC
from loguru import logger

from vikit.video.video import Video
from vikit.video.video_build_settings import VideoBuildSettings


class is_composite_video(ABC):
    @abstractmethod
    def is_composite_video(self):
        pass


# from vikit.video.composite_video import CompositeVideo


def build_using_local_resources(
    video, video_build_order, build_settings: VideoBuildSettings
):
    """
    Build the video locally

    params:
        video: The video to build
        video_build_order (list): The build order
        build_settings: The build settings

    Returns:
        list: The build order
    """
    pass


def build_using_cloud(video, video_build_order, build_settings: VideoBuildSettings):
    """
    Build the video remotely

    params:
        video: The video to build
        video_build_order (list): The build order
        build_settings: The build settings

    Returns:
        list: The build order
    """
    pass


def get_first_videos_first_build_order(
    video_build_order,
    video_tree,
    build_settings: VideoBuildSettings,
    already_added: set,
):
    """
    Get the first videos first build order

    Here we generate the video so that the  first composites or leaves
    (probably corresponding to the first prompts chunks) are generated first,
    aiming at showing something to the user as soon as possible. This is a graph deep traversal algorithm

    params:
        video_tree (list): The video tree to recurse on to parse the tree and get the build order
        build_settings: The build settings
        already_added (set): The set of already added videos

    Returns:
        list: The build order
    """
    video_build_order = []
    for video in video_tree:
        # if isinstance(CompositeVideo, video):
        if video.video_list and len(video.video_list) > 0:
            video_build_order.append(
                get_first_videos_first_build_order(
                    video_build_order, video.video_list, build_settings, already_added
                )
            )
        if video.id not in already_added:
            video_build_order.append(video)
            already_added.add(video.id)

    return video_build_order


def get_lazy_dependency_chain_build_order(
    video_tree: list[Video],
    build_settings: VideoBuildSettings,
    already_added: set,
    video_build_order: list[Video] = [],
):
    """
    Get the first videos first build order

    Here we generate the video in a lazy way, starting from the leaf composite and
    going up to the root composite as depency resolution is done

    params:
        video_tree (list): The video tree to recurse on to parse the tree and get the build order
        build_settings: The build settings
        already_added (set): The set of already added videos

    Returns:
        list: The build order
    """
    for video in video_tree:
        logger.debug(f"type(video) is {type(video)}")
        if isinstance(video, is_composite_video) and len(video.video_list) > 0:
            logger.debug(f"Going down the dependency chain for {video.id}")
            get_lazy_dependency_chain_build_order(
                video_build_order=video_build_order,
                video_tree=video.video_list,
                build_settings=build_settings,
                already_added=already_added,
            )
        else:  # on a leaf, we need to check if the video has dependencies
            if len(video.video_dependencies) > 0:
                logger.debug(f"On a leaf, going up the dependency chain for {video.id}")
                # go up the dependency chain
                get_lazy_dependency_chain_build_order(
                    video_build_order=video_build_order,
                    video_tree=video.video_dependencies,
                    build_settings=build_settings,
                    already_added=already_added,
                )
        if video.id not in already_added:
            logger.debug(f"Adding video {video.id} to the build order")
            video_build_order.append(video)
            already_added.add(video.id)

    return video_build_order
