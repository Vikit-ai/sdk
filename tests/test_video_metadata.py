import unittest
import warnings
import pytest

from vikit.video.video_metadata import VideoMetadata
from vikit.video.raw_text_based_video import RawTextBasedVideo


class TestMetaData(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        warnings.simplefilter("ignore", category=DeprecationWarning)
        DeprecationWarning

    @pytest.mark.unit
    def test_metadata_initial_setup(self):
        video = RawTextBasedVideo(raw_text_prompt="test", title="test")
        assert video.metadata is not None

    @pytest.mark.unit
    def test_metadata_get_set(self):
        video = RawTextBasedVideo(raw_text_prompt="test", title="test")
        video.metadata["key"] = "value"
        assert video.metadata["key"] == "value"

    @pytest.mark.unit
    def test_metadata_update(self):
        video = RawTextBasedVideo(raw_text_prompt="test", title="test")
        video.metadata.is_bg_music_generated = True
        assert video.metadata.is_bg_music_generated

    @pytest.mark.unit
    def test_metadata_delete(self):
        video = RawTextBasedVideo(raw_text_prompt="test", title="test")
        video.metadata["key"] = "value"
        del video.metadata["key"]
        assert not hasattr(video.metadata, "key")

    @pytest.mark.unit
    def test_metadata_cannot_delete_inner_attributes(self):
        video = RawTextBasedVideo(raw_text_prompt="test", title="test")
        video.metadata.is_bg_music_generated = True
        with pytest.raises(AttributeError):
            del video.metadata["is_bg_music_generated"]
