import os

TESTS_MEDIA_FOLDER = "medias"
TRANSITION_BOY_IN_TRAIN = "transition_[seine]_from_Travel_to_travel.mp4"
SAMPLE_RECORDED_PROMPT_MEANINGLESS_LIFE = "upload.mp3"
SMALL_CAT_VIDEO_FILE_NAME = "chat_video_super8.mp4"
GENERATED_3S_FOREST_VIDEO_SAMPLE_1 = "forest.mp4"
GENERATED_3S_FOREST_VIDEO_SAMPLE__2 = "treasures.mp4"
GENERATED_TRANSITION_FOREST_TREASURE_VIDEO_SAMPLE = (
    "transition_[seine]_from_treasures_to_forest.mp4"
)
TEST_PROMPT_RECORDING = "medias/test.mp3"
TEST_PROMPT_RECORDING_TRAIN_BOY = "sub_audio_for_subtitle_from_0_to_13.mp3"
TEST_PROMPT_RECORDING_STONES_TRAIN_BOY = "sub_audio_for_subtitle_from_0_to_14.mp3"
SAMPLE_GENERATED_MUSIC = "knowledgeStones_Forest_Symbols.mp3"
SAMPLE_GENERATED_BG_MUSIC = "PodcastSerenity.mp3"

_media_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), TESTS_MEDIA_FOLDER
)


def get_sample_gen_background_music():
    return os.path.join(_media_dir, SAMPLE_GENERATED_BG_MUSIC)


def get_cat_video_path():
    return os.path.join(_media_dir, SMALL_CAT_VIDEO_FILE_NAME)


def get_sample_generated_music_path():
    return os.path.join(_media_dir, SAMPLE_GENERATED_MUSIC)


def get_audio_slice():
    return os.path.join(_media_dir, "sub_audio_for_subtitle_from_0_to_13.mp3")


def get_generated_3s_forest_video_1_path():
    """
    Return the path to the generated 3s forest video sample usually used as start
    """
    return os.path.join(_media_dir, GENERATED_3S_FOREST_VIDEO_SAMPLE_1)


def get_generated_3s_forest_video_2_path():
    """
    Return the path to the generated 3s forest video sample usually used as end
    """
    return os.path.join(_media_dir, GENERATED_3S_FOREST_VIDEO_SAMPLE__2)


def get_test_prompt_recording():
    """
    Return the path of a short prompt recording
    """
    return os.path.join(_media_dir, TEST_PROMPT_RECORDING)


def get_test_prompt_recording_trainboy():
    """
    Return the path of a short prompt recording
    """
    return os.path.join(_media_dir, TEST_PROMPT_RECORDING_TRAIN_BOY)


def get_test_prompt_recording_stones_trainboy_path():
    """
    Return the path of a short prompt recording for Stones and trainboy
    """
    return os.path.join(_media_dir, TEST_PROMPT_RECORDING_STONES_TRAIN_BOY)


def get_test_transition_stones_trainboy_path():
    return os.path.join(_media_dir, TRANSITION_BOY_IN_TRAIN)


def get_test_recorded_prompt_path():
    return os.path.join(_media_dir, SAMPLE_RECORDED_PROMPT_MEANINGLESS_LIFE)
