# Copyright 2024 Vikit.ai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from vikit.common.GeneralBuildSettings import GeneralBuildSettings
from vikit.gateways.ML_models_gateway import MLModelsGateway
from vikit.gateways.ML_models_gateway_factory import MLModelsGatewayFactory


class PromptBuildSettings(GeneralBuildSettings):
    def __init__(
        self,
        delete_interim_files: bool = False,
        test_mode: bool = True,
        ml_models_gateway: MLModelsGateway = None,
        generate_from_llm_keyword: bool = False,  # Ask to generate the video by generating keywords from a LLM Prompt
        generate_from_llm_prompt: bool = True,
        **kwargs
    ):

        super().__init__(
            delete_interim_files=delete_interim_files,
            test_mode=test_mode,
        )

        self._ml_models_gateway = ml_models_gateway
        self.generate_from_llm_keyword = generate_from_llm_keyword
        self.generate_from_llm_prompt = generate_from_llm_prompt
        # self.excluded_words = ""
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
