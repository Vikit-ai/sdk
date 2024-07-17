import pytest


import vikit.gateways.fake_ML_models_gateway as fake_ML_models_gateway


class TestFakeMLGateway:

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_subtitles(self):
        subs = fake_ML_models_gateway.FakeMLModelsGateway().get_subtitles("test.mp3")
        assert subs is not None
        assert len(subs) > 0
