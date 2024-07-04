import pytest
import unittest
import warnings
import datetime
import uuid

from vikit.common.context_managers import WorkingFolderContext

from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.video_types import VideoType
from vikit.video.video_build_settings import VideoBuildSettings
from vikit.video.video_file_name import VideoFileName
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.video.composite_video import CompositeVideo
from vikit.prompt.prompt_factory import PromptFactory
from vikit.video.transition import Transition
from vikit.video.video_metadata import VideoMetadata


class TestVideoFileNames(unittest.TestCase):
    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    @pytest.mark.unit
    def test_nominal_file_name(self):
        # Create a VideoFileName instance with sample values

        bld_set = VideoBuildSettings()
        bld_set._id = "1234567890"
        bld_set._build_date = datetime.date(2024, 7, 1)
        bld_set._build_time = datetime.time(23, 4, 42)

        video_file_name = VideoFileName(
            build_settings=bld_set,
            video_metadata=VideoMetadata(
                title="Sample Video",
            ),
            video_type="comproot",
            video_features="dorio",
        )

        # Check if the file name is generated correctly
        expected_file_name = (
            "Sample Video_comproot_dorio_1234567890_2024-07-01_23:04:42_UID_"
            + str(video_file_name.unique_id)
            + ".mp4"
        )
        self.assertEqual(video_file_name.file_name, expected_file_name)

    @pytest.mark.unit
    def test_none_input(self):
        with self.assertRaises(ValueError):
            _ = VideoFileName(build_settings=None, video_metadata=None)

    @pytest.mark.unit
    def test_raw_text_video_file_name(self):
        """
        Test if the file name of a RawTextBasedVideo instance is generated correctly

        Here we expect the name to conform to the general video file name format.
        """
        raw_text_video = RawTextBasedVideo(raw_text_prompt="test prompt")

        fname = str(
            raw_text_video.get_target_file_name(build_settings=VideoBuildSettings()),
        )
        assert VideoFileName.is_video_file_name(
            fname
        ), "The file name of the RawTextBasedVideo instance is not valid. Generated file name: {}".format(
            fname
        )

    @pytest.mark.unit
    def test_from_file_name(self):
        id = str(uuid.uuid4())
        file_name = (
            f"exampletitle_comproot_ooooo_1234567890_2022-01-01_12:00_UID_{id}.mp4"
        )
        video_file_name = VideoFileName.from_file_name(file_name=file_name)
        assert video_file_name.title == "exampletitle"
        assert video_file_name.video_type == "comproot"
        assert video_file_name.video_features == "ooooo"
        assert video_file_name.build_id == "1234567890"
        assert video_file_name._build_date == datetime.date(2022, 1, 1)
        assert video_file_name._build_time == datetime.time(12, 0)
        assert video_file_name.unique_id == uuid.UUID(id)

    @pytest.mark.unit
    def test_extract_features(self):

        bld_set = VideoBuildSettings()
        bld_set._id = "1234567890"
        bld_set._build_date = datetime.date(2024, 7, 1)
        bld_set._build_time = datetime.time(23, 4, 42)

        video_file_name = VideoFileName(
            video_metadata=VideoMetadata(title="Sample Video"),
            build_settings=bld_set,
            video_type="comproot",
            video_features="dogrs",
            file_extension="mp4",
        )
        # Extract the features
        extracted_features = video_file_name.extract_features_as_string()
        # Check if the extracted features are correct
        self.assertEqual(extracted_features, "dogrs")

    @pytest.mark.unit
    def test_extract_features_no_features(self):

        bld_set = VideoBuildSettings()
        bld_set._id = "1234567890"
        bld_set._build_date = datetime.date(2024, 7, 1)
        bld_set._build_time = datetime.time(23, 4, 42)
        bld_set.music_building_context.apply_background_music = False
        bld_set.interpolate = False

        video_file_name = VideoFileName(
            video_metadata=VideoMetadata(title="Sample Video"),
            build_settings=bld_set,
            video_type="comproot",
            file_extension="mp4",
        )
        # Extract the features
        extracted_features = video_file_name.extract_features_as_string()
        # Check if the extracted features are correct
        expected_features = "ooooo"
        self.assertEqual(extracted_features, expected_features)

    def get_test_build_settings(self):
        bld_set = VideoBuildSettings()
        bld_set.test_mode = True
        bld_set._id = "1234567890"
        bld_set._build_date = datetime.date(2024, 7, 1)
        bld_set._build_time = datetime.time(23, 4, 42)
        bld_set.output_path = "output_path"
        bld_set.include_audio_subtitles = False
        bld_set.interpolate = False
        bld_set.music_building_context.apply_background_music = True
        bld_set.music_building_context.generate_background_music = True

        return bld_set

    @pytest.mark.local_integration
    def test_root_composite_video_file_name(self):
        """
        Test if the file name of a root composite video is generated correctly

        Here we expect the name to conform to the general video file name format:
        - video type as rootcomp
        - video features as goooo

        """
        with WorkingFolderContext():
            composite_video = CompositeVideo()
            bld_set = self.get_test_build_settings()
            fname = str(composite_video.get_target_file_name(build_settings=bld_set))
            vid_fname = VideoFileName.from_file_name(fname)

            assert VideoFileName.is_video_file_name(
                fname
            ), "The file name of the RawTextBasedVideo instance is not valid. Generated file name: {}".format(
                fname
            )

            assert vid_fname.video_type == str(
                VideoType.COMPROOT
            ), "The video type is not correct, {}. Returned: ".format(
                vid_fname.video_type
            )
            assert (
                vid_fname.video_features == "goooo"
            ), "The video features are not correct: features returned: {}".format(
                vid_fname.video_features
            )
            assert (
                vid_fname.build_id == "1234567890"
            ), "The build ID is not correct, {}".format(bld_set.id)
            assert vid_fname._build_date == bld_set.build_date
            assert vid_fname._build_time == bld_set.build_time
            assert vid_fname.unique_id is not None

    @pytest.mark.local_integration
    def test_child_composite_video_file_name(self):

        with WorkingFolderContext():
            root_composite_video = CompositeVideo()
            child_composite_video = CompositeVideo()
            root_composite_video.append_video(child_composite_video)
            bld_set = self.get_test_build_settings()

            fname = str(
                child_composite_video.get_target_file_name(build_settings=bld_set)
            )
            vid_fname = VideoFileName.from_file_name(fname)

            assert VideoFileName.is_video_file_name(
                fname
            ), "The file name of the RawTextBasedVideo instance is not valid. Generated file name: {}".format(
                fname
            )

            assert vid_fname.video_type == str(
                VideoType.COMPCHILD
            ), "The video type is not correct, {}. Returned: ".format(
                vid_fname.video_type
            )
            assert (
                vid_fname.video_features == "goooo"
            ), "The video features are not correct: features returned: {}".format(
                vid_fname.video_features
            )
            assert (
                vid_fname.build_id == "1234567890"
            ), "The build ID is not correct, {}".format(bld_set.id)
            assert vid_fname._build_date == bld_set.build_date
            assert vid_fname._build_time == bld_set.build_time
            assert vid_fname.unique_id is not None

    @pytest.mark.local_integration
    def test_prompt_based_video_file_name(self):
        with WorkingFolderContext():
            bld_set = self.get_test_build_settings()
            prpt_vid = PromptBasedVideo(
                prompt=PromptFactory(
                    ml_gateway=bld_set.get_ml_models_gateway()
                ).create_prompt_from_text("test of prompt that last a few seconds")
            )
            fname = str(prpt_vid.get_target_file_name(build_settings=bld_set))
            vid_fname = VideoFileName.from_file_name(fname)

            assert VideoFileName.is_video_file_name(
                fname
            ), "The file name of the PromptBasedVideo instance is not valid. Generated file name: {}".format(
                fname
            )

            assert vid_fname.video_type == str(
                VideoType.PRMPTBASD
            ), "The video type is not correct, {}. Returned: ".format(
                vid_fname.video_type
            )
            assert (
                vid_fname.video_features == "goooo"
            ), "The video features are not correct: features returned: {}".format(
                vid_fname.video_features
            )
            assert (
                vid_fname.build_id == "1234567890"
            ), "The build ID is not correct, {}".format(bld_set.id)
            assert vid_fname._build_date == bld_set.build_date
            assert vid_fname._build_time == bld_set.build_time
            assert vid_fname.unique_id is not None

    @pytest.mark.local_integration
    def test_transition_video_file_name(self):
        with WorkingFolderContext():
            trans_vid = Transition(RawTextBasedVideo("test"), RawTextBasedVideo("test"))
            bld_set = self.get_test_build_settings()
            fname = trans_vid.get_target_file_name(build_settings=bld_set)
            vid_fname = VideoFileName.from_file_name(fname)

            assert vid_fname.video_type == str(VideoType.TRANSITION)
            assert (
                vid_fname.video_features == "goooo"
            ), "The video features are not correct: features returned: {}".format(
                vid_fname.video_features
            )
            assert (
                vid_fname.build_id == "1234567890"
            ), "The build ID is not correct, {}".format(bld_set.id)
            assert vid_fname._build_date == bld_set.build_date
            assert vid_fname._build_time == bld_set.build_time
            assert vid_fname.unique_id is not None
