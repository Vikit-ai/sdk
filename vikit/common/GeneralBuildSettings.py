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

import datetime
from random import randint

import vikit.gateways.ML_models_gateway_factory as mlfactory


class GeneralBuildSettings:

    def __init__(
        self,
        delete_interim_files: bool = False,  # not implemented yet :)
        test_mode: bool = False,
        target_dir_path: str = None,
        target_file_name: str = None,
        vikit_api_key: str = None,
    ):
        """
        Initialize the build settings

        Args:
            delete_interim_files: whether to delete the intermediate video files, first and last frames
            test_mode: whether to run the video generation in local mode, to run local and fast tests
            output_path: the path where the video will be saved, could be local or remote (i.e. a cloud bucket or a streaming service)
            output_file_name: the final output file name
        """
        self.delete_interim_files = delete_interim_files  # Not deleting the intermediate video files, first and last frames TODO: to be implemented
        # and any other resources is useful for debugging purposes and to reuse the data for further
        # video combinations, model trainings
        self.test_mode = test_mode  # Run the video generation in local mode, to run local and fast tests
        self._ml_models_gateway = None
        self.id = str(randint(1, 9999999999)).zfill(10)
        self.build_date = datetime.date.today().strftime("%Y-%m-%d")
        self.build_time = datetime.datetime.now().time().strftime("%H:%M")
        self.target_dir_path = target_dir_path
        self.target_file_name = target_file_name
        self.vikit_api_key = vikit_api_key

    def get_ml_models_gateway(self):
        """
        Handy function to get the ML models gateway from the buildsettings, as it is used in many places
        like a context
        """
        if self._ml_models_gateway is None:
            self._ml_models_gateway = (
                mlfactory.MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=self.test_mode,
                    vikit_api_key=self.vikit_api_key
                )
            )
        return self._ml_models_gateway

    @property
    def output_path(self) -> str:
        """
        Get the output path where the video will be saved
        """
        return self.target_dir_path

    @output_path.setter
    def output_path(self, output_path: str):
        """
        Set the output path where the video will be saved
        """
        self.target_dir_path = output_path

        return self
