import os
from abc import abstractmethod, ABC
from concurrent.futures import ProcessPoolExecutor

from loguru import logger

from vikit.video.video import Video
from vikit.video.video_build_settings import VideoBuildSettings
import vikit.common.config as config
from vikit.wrappers.ffmpeg_wrapper import (
    concatenate_videos,
    reencode_video,
)


class is_composite_video(ABC):
    @abstractmethod
    def is_composite_video(self):
        pass


# from vikit.video.composite_video import CompositeVideo


async def build_using_local_resources(
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
    return await local_build_strategy(
        composite_video=video, build_settings=build_settings
    )


async def local_build_strategy(composite_video, build_settings: VideoBuildSettings):
    """
    Build the composite video locally

    params:
        build_settings: The settings to be used for the build

    returns:
        self: The current object
    """
    short_title = composite_video.get_title()
    # TODO: change this hard truncate!!
    if len(short_title) > 20:
        short_title = short_title[:20]

    video_list_file = "_".join(
        [
            short_title,
            config.get_video_list_file_name(),
        ]
    )

    cascaded_build_settings = VideoBuildSettings(  # we will handle the background only at the video composite root level
        include_audio_read_subtitles=False,  # we will handle the subtitles only at the video composite root level
        test_mode=build_settings.test_mode,
        run_async=build_settings.run_async,
    )

    # Generate the videos
    composite_video._video_list = process_videos(
        build_settings=cascaded_build_settings,
        video_list=composite_video.video_list,
        function_to_invoke=composite_video._process_gen_vid_bins,
    )
    nb_interpolated = len(
        list(
            filter(
                lambda builtvideo: builtvideo.metadata.is_interpolated,
                composite_video._video_list,
            )
        )
    )

    if nb_interpolated < len(composite_video._video_list):
        composite_video.metadata.is_interpolated
    elif nb_interpolated == 0:
        composite_video.metadata.is_interpolated = False
        # TODO: handle partially interpolated videos, not really importnat for now

    ratio = composite_video._get_ratio_to_multiply_animations(
        build_settings=build_settings, video_composite=composite_video
    )
    if composite_video._needs_reencoding:
        composite_video._video_list = process_videos(
            build_settings=cascaded_build_settings,  # We take the freshly generated videos as input param
            video_list=composite_video.video_list,
            function_to_invoke=reencode_video,
        )
        composite_video.metadata.is_reencoded = True

    # We have the final file names (they may have changed between initial video instanciation and
    # inference of a name after querying an LLM
    with open(video_list_file, "w") as myfile:
        for video in composite_video.video_list:
            file_name = video._media_url
            myfile.write("file " + file_name + os.linesep)

    composite_video._media_url = concatenate_videos(
        input_file=os.path.abspath(video_list_file),
        target_file_name=composite_video.get_file_name_by_state(
            build_settings=build_settings
        ),
        ratioToMultiplyAnimations=ratio,
    )  # keeping one consistent file name

    composite_video._is_video_generated = True
    return composite_video


def process_videos(
    build_settings: VideoBuildSettings,
    video_list,
    function_to_invoke,
    proc_pool_executor=None,
):
    """
    Process the videos asynchronously

    Args:
        build_settings (VideoBuildSettings): The build settings
        video_list (list): The list of videos
        function_to_invoke (function): The function to invoke

    Returns:
        list: The list of processed videos
    """
    if build_settings.run_async:
        logger.debug(
            f"Processing videos asynchronously, run_async: {build_settings.run_async}"
        )
        results = []
        if not proc_pool_executor:
            proc_pool_executor = ProcessPoolExecutor()

        for video in video_list:
            # TODO: you may have spotted that here we are not really processing the videos asynchronously, this caused some issues
            # for the 0.1 so we will imporve this in the next version, doing a map on the video_list
            results.extend(
                proc_pool_executor.map(
                    function_to_invoke,
                    [(video, build_settings, video.media_url)],
                )
            )
    else:
        logger.debug(
            f"Processing videos synchronously, run_async: {build_settings.run_async}"
        )
        results = []
        for video in video_list:
            results.extend(
                [
                    function_to_invoke(
                        (
                            video,
                            build_settings,
                            video.media_url,
                            video.get_file_name_by_state(build_settings=build_settings),
                        )
                    )
                ]
            )

    return results


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
    video_tree: list[Video],
    build_settings: VideoBuildSettings,
    already_added: set,
    video_build_order: list[Video] = [],
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
    for video in video_tree:
        if isinstance(video, is_composite_video) and len(video.video_list) > 0:
            logger.trace(f"Going down the dependency chain for {video.id}")
            get_first_videos_first_build_order(
                video_build_order=video_build_order,
                video_tree=video.video_list,
                build_settings=build_settings,
                already_added=already_added,
            )
        if video.id not in already_added:
            logger.debug(f"Adding video {video.id} to the build order")
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
