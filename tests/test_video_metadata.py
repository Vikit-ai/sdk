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

import warnings

import pytest

from vikit.video.raw_text_based_video import RawTextBasedVideo


class TestMetaData:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        warnings.simplefilter("ignore", category=DeprecationWarning)
        DeprecationWarning

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_metadata_initial_setup(self):
        video = RawTextBasedVideo(raw_text_prompt="test", title="test")
        assert video.metadata is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_metadata_get_set(self):
        video = RawTextBasedVideo(raw_text_prompt="test", title="test")
        video.metadata["key"] = "value"
        assert video.metadata["key"] == "value"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_metadata_update(self):
        video = RawTextBasedVideo(raw_text_prompt="test", title="test")
        video.metadata.is_bg_music_generated = True
        assert video.metadata.is_bg_music_generated

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_metadata_delete(self):
        video = RawTextBasedVideo(raw_text_prompt="test", title="test")
        video.metadata["key"] = "value"
        del video.metadata["key"]
        assert not hasattr(video.metadata, "key")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_metadata_cannot_delete_inner_attributes(self):
        video = RawTextBasedVideo(raw_text_prompt="test", title="test")
        video.metadata.is_bg_music_generated = True
        with pytest.raises(AttributeError):
            del video.metadata["is_bg_music_generated"]
