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
        generate_from_llm_keyword: bool = False,  # Ask to generate the video by generating keywords from a LLM Prompt
        generate_from_llm_prompt: bool = True,
        model_provider: str = None,
        **kwargs
    ):

        super().__init__(
            delete_interim_files=delete_interim_files,
        )
        self.model_provider=model_provider
        self.generate_from_llm_keyword = generate_from_llm_keyword
        self.generate_from_llm_prompt = generate_from_llm_prompt
        # self.excluded_words = ""
        self._additional_args = kwargs

