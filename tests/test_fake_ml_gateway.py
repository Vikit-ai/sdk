import vikit.gateways.fake_ML_models_gateway as fake_ML_models_gateway

import unittest


class TestFakeMLGateway(unittest.TestCase):

    def test_get_subtitles(self):
        subs = fake_ML_models_gateway.FakeMLModelsGateway().get_subtitles("test.mp3")
        assert subs is not None
        assert len(subs) > 0
