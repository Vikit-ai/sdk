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

from vikit.gateways.fake_ML_models_gateway import FakeMLModelsGateway
from vikit.gateways.vikit_gateway import VikitGateway


class MLModelsGatewayFactory:
    """
    ML models gateway factory helps getting the right sub class of ML models gateway depending on
    the input provided.
    """

    def get_ml_models_gateway(self, test_mode: bool = False, vikit_api_key: str=None):
        if test_mode:
            return FakeMLModelsGateway()
        else:
            return VikitGateway(vikit_api_key)
