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

import pytest

from tests.testing_medias import get_paris_subtitle_file, get_paris_video
from vikit.common.context_managers import WorkingFolderContext
from vikit.postprocessing.video_subtitle_renderer import VideoSubtitleRenderer

PARIS_VIDEO = get_paris_video()
SUBTITLE_PATH = get_paris_subtitle_file()


class TestPostProcessing:
    @pytest.mark.local_integration
    def test_render_subtitle(self):
        with WorkingFolderContext():

            subtitle_writer = VideoSubtitleRenderer()
            subtitle_writer.add_subtitles_to_video(
                input_video_path=PARIS_VIDEO,
                subtitle_srt_filepath=SUBTITLE_PATH,
                output_video_path="Video_with_subtitle.mp4",
            )
