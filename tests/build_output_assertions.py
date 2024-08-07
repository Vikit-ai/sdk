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

from vikit.video.video_file_name import VideoFileName
from vikit.video.video_types import VideoType


class BuildOutputAssertor():

    def __init__(self, files: list[str]):
        """
        Initializes the list of file names to work upon in one pass

        params:
            files: The list of file names to work upon

        """
        self._files = files
        self._generated_videos = []
        self._root_composite_videos = []
        self._child_composite_videos = []
        self._raw_text_videos = []
        self._transitions = []
        self._prompt_based_videos = []
        self._imported_videos = []
        self._anomaly = False
        self._subtitles = []


    def parse_files(self):
        for file in self._files:
            if VideoFileName.is_video_file_name():
                fname = VideoFileName().from_file_name(file)

                if fname.video_type == VideoType.GENERATED:
                    self._generated_videos.append(file)

                if fname.video_type == VideoType.COMPCHILD:
                    self._child_composite_videos.append(file)

                if fname.video_type == VideoType.COMPROOT:
                    self._root_composite_videos = file

                if fname.video_type == VideoType.IMPORTED:
                    self._imported_videos.append(file)

                if fname.video_type == VideoType.PRMPTBASD:
                    self._prompt_based_videos.append(file)

                if fname.video_type == VideoType.RAWTEXT:
                    self._raw_text_videos.append(file)

                if fname.video_type == VideoType.TRANSITION:
                    self._transitions.append(file)
                    
                if fname.video_type == "undefined":
                    self._anomaly = True
            else:
                if file.__contains__("subtitle") or file.__contains__("srt"):
                    self._subtitles.append(file)

    def assert_no_anomaly(self):
        """
        Check that no anomaly has been detected
        """
        if len(self._root_composite_videos) > 1: 
            self._anomaly = True

        assert not self._anomaly, "Anomaly detected in the file list"

    def assert_exists_generated_video(self, nb_files_expected):
        """
        Check that the number of generated video files is as expected

        Generated videos are supposed to be named as follows:
        - <video_title>_generated_*.mp4
        """
        assert len(self._generated_videos) == nb_files_expected, f"Expected {nb_files_expected} generated videos, found {len(self._generated_videos)}"


    def assert_exists_transitions(self, nb_files_expected):
        """
        Check that the number of transition video files is as expected

        Transition videos are supposed to be named as follows:
        - <video_title>_transition_*.mp4
        """
        assert len(self._transitions) == nb_files_expected, f"Expected {nb_files_expected} transition videos, found {len(self._transitions)}"

    def assert_exists_child_composite_videos(self, nb_files_expected):
        """
        Check that the number of composite video files is as expected

        Composite videos are supposed to be named as follows:
        - <video_title>_comp-*.mp4
        """
        assert len(self._child_composite_videos) == nb_files_expected, f"Expected {nb_files_expected} composite videos, found {len(self._child_composite_videos)}"

    def assert_exists_root_composite_videos(self, nb_files_expected):
        """
        Check that the number of composite video files is as expected

        Composite videos are supposed to be named as follows:
        - <video_title>_comp-*.mp4
        """
        assert len(self._root_composite_videos) == nb_files_expected, f"Expected {nb_files_expected} composite videos, found {len(self._root_composite_videos)}"

    def assert_exists_imported_videos(self, nb_files_expected):
        """
        Check that the number of imported video files is as expected

        Imported videos are supposed to be named as follows:
        - <video_title>_imported_*.mp4
        """
        assert len(self._imported_videos) == nb_files_expected, f"Expected {nb_files_expected} imported videos, found {len(self._imported_videos)}"

    def assert_exists_prompt_based_videos(self, nb_files_expected):
        """
        Check that the number of prompt based video files is as expected

        Prompt based videos are supposed to be named as follows:
        - <video_title>_prmpt_basd_*.mp4
        """
        assert len(self._prompt_based_videos) == nb_files_expected, f"Expected {nb_files_expected} prompt based videos, found {len(self._prompt_based_videos)}"

    def assert_exists_raw_text_videos(self, nb_files_expected):
        """
        Check that the number of raw text video files is as expected

        Raw text videos are supposed to be named as follows:
        - <video_title>_raw-text_*.mp4
        """
        assert len(self._raw_text_videos) == nb_files_expected, f"Expected {nb_files_expected} raw text videos, found {len(self._raw_text_videos)}" 


    def assert_exists_subtitle(self, nb_files_expected):
        """
        Check that the number of subtitle files is as expected
        """
        if len(self._subtitles) != nb_files_expected:
            print("Found subtitle files: ", self._subtitle)

    def assert_exists_generated_audio_prompt(self, nb_files_expected):
    pass


    def assert_exists_generated_bg_music(self, nb_files_expected):
    pass


    def assert_exists_default_bg_music(self, nb_files_expected):
    pass
