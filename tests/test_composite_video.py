import unittest
import warnings

import pytest
from loguru import logger

import tests.tests_medias as test_media
from vikit.video.video import Video, VideoBuildSettings
from vikit.video.composite_video import CompositeVideo
from vikit.common.context_managers import WorkingFolderContext
from vikit.video.raw_text_based_video import RawTextBasedVideo
import tests.tests_tools as tools  # used to get a library of test prompts
import vikit.wrappers.ffmpeg_wrapper as ffmpegwrapper
from vikit.music import MusicBuildingContext
from tests.tests_tools import test_prompt_library
from vikit.video.imported_video import ImportedVideo

from tests.tests_medias import (
    get_cat_video_path,
    get_test_transition_stones_trainboy_path,
)

prompt_mystic = tools.test_prompt_library["moss_stones-train_boy"]


class TestCompositeVideo(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.sample_cat_video_path = test_media.get_cat_video_path()
        self.prompt_loosing_faith = None

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    def test_create_video_mix_with_empty_video(self):
        video = None
        test_video_mixer = CompositeVideo()
        # we expect an exception here
        with pytest.raises(ValueError):
            test_video_mixer.append_video(video)

    def test_create_single_video_mix_single_video(self):
        """
        Create a single video mix
        No Music
        """
        with pytest.raises(TypeError):
            _ = Video()

    @pytest.mark.local_integration
    def test_create_video_mix_with_preexiting_video_bin_default_bkg_music_subtitles_tired_life(
        self,
    ):
        with WorkingFolderContext():
            video = ImportedVideo(self.sample_cat_video_path)
            assert video.media_url, "Media URL should not be null"
            test_video_mixer = CompositeVideo()
            test_video_mixer.append_video(video)
            built = test_video_mixer.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        generate_background_music=True
                    ),
                    test_mode=True,
                    include_audio_read_subtitles=True,
                    prompt=tools.test_prompt_library["tired"],
                )
            )

            assert built.media_url is not None

    @pytest.mark.local_integration
    def test_int_create_video_mix_with_preexiting_video_bin_no_bkg_music(self):
        with WorkingFolderContext():
            video = ImportedVideo(self.sample_cat_video_path)
            test_video_mixer = CompositeVideo()
            test_video_mixer.append_video(video)
            test_video_mixer.build()
            logger.debug(
                f"Test video mix with preexisting video bin: {test_video_mixer}"
            )
            assert test_video_mixer.media_url is not None

    @pytest.mark.local_integration
    def test_combine_generated_and_preexiting_video_based_video(self):
        with WorkingFolderContext():
            video = RawTextBasedVideo(
                tools.test_prompt_library["moss_stones-train_boy"].text
            )
            video_imp = ImportedVideo(self.sample_cat_video_path)
            test_video_mixer = CompositeVideo()
            test_video_mixer.append_video(video).append_video(video_imp)
            test_video_mixer.build(VideoBuildSettings(test_mode=True))

            assert test_video_mixer.media_url is not None

    @pytest.mark.local_integration
    def test_build_video_composite_2_prompt_vids_music_no_subs_no_transition(self):
        with WorkingFolderContext():
            test_prompt = prompt_mystic
            raw_text_video = RawTextBasedVideo(test_prompt.text)
            test_video_mixer = CompositeVideo()
            test_video_mixer.append_video(raw_text_video).append_video(raw_text_video)
            test_video_mixer.build(
                VideoBuildSettings(
                    test_mode=True,
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=True
                    ),
                )
            )
            assert (
                test_video_mixer.media_url is not None
            ), "Media URL should not be null"
            assert (
                test_video_mixer.background_music
            ), "Background music should not be null"

    @pytest.mark.local_integration
    def test_build_video_composite_with_default_bkg_music_and_audio_subtitle(self):
        with WorkingFolderContext():
            video_start = ImportedVideo(get_cat_video_path())
            video_end = ImportedVideo(get_test_transition_stones_trainboy_path())
            test_video_mixer = CompositeVideo()
            final_video = (
                test_video_mixer.append_video(video_start)
                .append_video(video_end)
                .append_video(CompositeVideo())  # should be filtered
            )
            final_video = final_video.build(
                VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True,
                        generate_background_music=False,
                    ),
                    include_audio_read_subtitles=False,
                    prompt=test_prompt_library["moss_stones-train_boy"],
                )
            )
            assert final_video.media_url is not None
            assert final_video.background_music is not None

    @pytest.mark.local_integration
    def test_prompt_recording_synchro_tired(self):
        with WorkingFolderContext():
            prompt_with_recording = tools.test_prompt_library["tired"]
            final_composite_video = CompositeVideo()
            for subtitle in prompt_with_recording.subtitles:
                video = RawTextBasedVideo(subtitle.text)
                # video.build(build_settings=VideoBuildSettings(test_mode=True))
                final_composite_video.append_video(video)

            final_composite_video.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        generate_background_music=False, apply_background_music=True
                    ),
                    test_mode=True,
                    include_audio_read_subtitles=False,
                    prompt=prompt_with_recording,
                )
            )

    @pytest.mark.local_integration
    def test_use_recording_ratio_on_existing_gen_default_bg_music_include_subs_loseFaitprompt(
        self,
    ):
        """
        Create a single video mix with 2 imported video initially nade from gen video
        and use default bg music
        """
        with WorkingFolderContext():
            vid1 = ImportedVideo(test_media.get_generated_3s_forest_video_1_path())
            vid2 = ImportedVideo(test_media.get_generated_3s_forest_video_2_path())

            video_comp = CompositeVideo()
            video_comp.append_video(vid1).append_video(vid2)
            video_comp.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        generate_background_music=False, apply_background_music=True
                    ),
                    include_audio_read_subtitles=True,
                    prompt=tools.test_prompt_library["tired"],
                )
            )

    @pytest.mark.local_integration
    @unittest.skip("This test is not working yet, lower priority for now")
    def test_video_build_expected_video_length(self):
        """
        Create a single video mix with 2 imported video initially nade from gen video
        and check the viddeo expected length is applied
        """
        with WorkingFolderContext():
            vid1 = ImportedVideo(test_media.get_generated_3s_forest_video_1_path())
            vid2 = ImportedVideo(test_media.get_generated_3s_forest_video_2_path())

            video_comp = CompositeVideo()
            video_comp.append_video(vid1).append_video(vid2)
            video_comp.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True
                    ),
                    include_audio_read_subtitles=True,
                    prompt=tools.test_prompt_library["tired"],
                    expected_length=5,
                )
            )
            assert ffmpegwrapper.get_media_duration(video_comp.media_url) == 5

    @pytest.mark.integration
    def test_int_combine_generated_and_preexiting_video_based_video_no_build_settings(
        self,
    ):
        with WorkingFolderContext():
            build_stgs = VideoBuildSettings(test_mode=False)
            test_prompt = tools.test_prompt_library["train_boy"]
            video = RawTextBasedVideo(test_prompt.text)
            video2 = ImportedVideo(self.sample_cat_video_path)
            test_video_mixer = CompositeVideo()
            test_video_mixer.append_video(video).append_video(video2)
            test_video_mixer.build(build_settings=build_stgs)

            assert test_video_mixer.media_url is not None

    @pytest.mark.local_integration
    def test_tired_local_no_transitions_with_music_and_prompts(self):

        with WorkingFolderContext():
            tired_prompt_with_recording = tools.create_fake_prompt_tired()
            final_composite_video = CompositeVideo()
            for subtitle in tired_prompt_with_recording.subtitles:
                video = RawTextBasedVideo(subtitle.text)
                video.build(build_settings=VideoBuildSettings(test_mode=True))
                final_composite_video.append_video(video)

            final_composite_video.build(
                build_settings=VideoBuildSettings(
                    music_building_context=MusicBuildingContext(
                        apply_background_music=True, generate_background_music=True
                    ),
                    test_mode=True,
                    include_audio_read_subtitles=True,
                    prompt=tired_prompt_with_recording,
                )
            )

    @pytest.mark.local_integration
    # @pytest.mark.non_regression
    def test_issue_6(self):
        """
        Transition between two compositve videos won't work #6
        https://github.com/leclem/aivideo/issues/6
        """
        with WorkingFolderContext():

            bld_settings = VideoBuildSettings(
                music_building_context=MusicBuildingContext(
                    apply_background_music=True, generate_background_music=True
                ),
                test_mode=True,
                include_audio_read_subtitles=True,
                prompt=test_prompt_library["train_boy"],
            )

            comp_start = CompositeVideo().append_video(
                ImportedVideo(test_media.get_cat_video_path())
            )
            comp_end = CompositeVideo().append_video(
                ImportedVideo(test_media.get_cat_video_path())
            )

            from vikit.video.seine_transition import SeineTransition

            transition = SeineTransition(comp_start, comp_end)

            vid_cp_final = CompositeVideo()

            vid_cp_final.append_video(comp_start).append_video(transition).append_video(
                comp_end
            )
            # with pytest.raises(AssertionError):
            vid_cp_final.build(build_settings=bld_settings)

    @pytest.mark.local_integration
    @pytest.mark.non_regression
    def test_issue_6_generated_subvids(self):
        """
        Transition between two compositve videos won't work #6
        https://github.com/leclem/aivideo/issues/6
        """
        with WorkingFolderContext():

            bld_settings = VideoBuildSettings(
                music_building_context=MusicBuildingContext(
                    apply_background_music=True, generate_background_music=True
                ),
                test_mode=True,
                include_audio_read_subtitles=True,
            )

            comp_start = CompositeVideo().append_video(
                RawTextBasedVideo(
                    "A young boy traveling in the train alongside Mediterranean coast"
                )
            )
            comp_end = CompositeVideo().append_video(
                RawTextBasedVideo(
                    "A group of ancient moss-covered stones come to life in an abandoned forest"
                )
            )

            from vikit.video.seine_transition import SeineTransition

            transition = SeineTransition(comp_start, comp_end)

            vid_cp_final = CompositeVideo()

            vid_cp_final.append_video(comp_start).append_video(transition).append_video(
                comp_end
            )
            # with pytest.raises(AssertionError):
            vid_cp_final.build(build_settings=bld_settings)
