import pytest

from tests.medias.references_for_tests import VIKIT_PITCH_MP4
from vikit.common.context_managers import WorkingFolderContext
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory
from vikit.video.building.handlers.video_reencoding_handler import (
    VideoReencodingHandler,
)
from vikit.video.imported_video import ImportedVideo


@pytest.fixture
async def setup_test():
    with WorkingFolderContext():
        test_gateway = MLModelsGatewayFactory().get_ml_models_gateway(test_mode=True)
        handler = VideoReencodingHandler()
        video = ImportedVideo(video_file_path=VIKIT_PITCH_MP4)
        yield test_gateway, handler, video


@pytest.mark.asyncio
@pytest.mark.local_integration
async def test_video_reencoding_handler(setup_test):
    test_gateway, handler, video = setup_test
    reencode_video = await handler.execute_async(video, test_gateway)

    assert reencode_video is not None, (
        f"Video built should not be None. This is the output {reencode_video}"
    )
    assert reencode_video.media_url is not None, (
        f"Video built should have a media url. This is the output {reencode_video}"
    )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_video_reencoding_no_reencode(setup_test):
    test_gateway, handler, video = setup_test
    video._needs_video_reencoding = False

    no_reencode_video = await handler.execute_async(video, test_gateway)

    assert no_reencode_video is not None, (
        f"Video built should not be None. This is the output {no_reencode_video}"
    )
    assert no_reencode_video.media_url is not None, (
        f"Video built should have a media url. This is the output {no_reencode_video}"
    )
