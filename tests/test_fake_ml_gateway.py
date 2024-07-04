import pytest
import unittest

import vikit.gateways.fake_ML_models_gateway as fake_ML_models_gateway


class TestFakeMLGateway(unittest.TestCase):

    @pytest.mark.unit
    def test_get_subtitles(self):
        subs = fake_ML_models_gateway.FakeMLModelsGateway().get_subtitles("test.mp3")
        assert subs is not None
        assert len(subs) > 0
