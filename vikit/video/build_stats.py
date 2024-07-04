import time

import vikit.video.video as Video


class BuildStats:
    """
    Stores and help measure the time taken to build a video.

    We do store the related video id and its top parent video id to help filter out the stats.

    Used to keep telemetry stats too, which means we will serialize this class and send it to the telemetry platform.
    """

    def __init__(self, video: Video = None):
        self.video_id = video.id if video is not None else id.null
        self.top_parent_video_id = video.id if video is not None else id.null

        self.end_time: float = None
        self.total_time: float = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()
        self.total_time = self.end_time - self.start_time
        return self.total_time
