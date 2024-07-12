import pytest
import unittest
import asyncio

import vikit.gateways.fake_ML_models_gateway as fake_ML_models_gateway


class TestFakeMLGateway(unittest.TestCase):

    @pytest.mark.unit
    async def test_get_subtitles(self):
        subs = await asyncio.gather(
            fake_ML_models_gateway.FakeMLModelsGateway().get_subtitles_async("test.mp3")
        )
        assert subs is not None
        assert len(subs) > 0
