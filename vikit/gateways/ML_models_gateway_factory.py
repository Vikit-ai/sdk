from vikit.gateways.vikit_gateway import VikitGateway
from vikit.gateways.fake_ML_models_gateway import FakeMLModelsGateway


class MLModelsGatewayFactory:
    """
    ML models gateway factory helps getting the right sub class of ML models gateway depending on
    the input provided.
    """

    def get_ml_models_gateway(self, test_mode: bool = True):
        if test_mode:
            return FakeMLModelsGateway()
        else:
            return VikitGateway()
