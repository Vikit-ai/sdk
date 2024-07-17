from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory
from vikit.common.GeneralBuildSettings import GeneralBuildSettings


class PromptBuildSettings(GeneralBuildSettings):
    def __init__(
        self,
        delete_interim_files: bool = False,
        run_async: bool = True,
        test_mode: bool = True,
        ml_models_gateway: MLModelsGateway = None,
        generate_from_llm_keyword: bool = False,  # Ask to generate the video by generating keywords from a LLM Prompt
        generate_from_llm_prompt: bool = True,
        **kwargs
    ):

        super().__init__(
            delete_interim_files=delete_interim_files,
            run_async=run_async,
            test_mode=test_mode,
        )

        self._ml_models_gateway = ml_models_gateway
        self.generate_from_llm_keyword = generate_from_llm_keyword
        self.generate_from_llm_prompt = generate_from_llm_prompt
        self._additional_args = kwargs

    def get_ml_models_gateway(self):
        """
        Handy function to get the ML models gateway from the buildsettings, as it is used in many places
        like a context
        """
        if self._ml_models_gateway is None:
            self._ml_models_gateway = MLModelsGatewayFactory().get_ml_models_gateway(
                test_mode=self.test_mode
            )
        return self._ml_models_gateway
