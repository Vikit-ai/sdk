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

import os

import warnings
import pytest
from loguru import logger

import vertexai
import google.generativeai as genai
from vertexai.generative_models import GenerativeModel
from google.cloud import secretmanager

PROJECT_ID = "aivideoproject"
SECRET_ID = "dev-google-gemini-api-key"


def get_secret(secret_id, project_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")


api_key = get_secret(SECRET_ID, PROJECT_ID)
genai.configure(api_key=api_key)


class TestGeminiIntegration:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        warnings.simplefilter("ignore", category=DeprecationWarning)

    @pytest.mark.integration
    async def test_chat_enhancement(self):
        logger.debug("test_chat_enhancement")
        model = genai.GenerativeModel("gemini-1.5-flash-8b")
        response = model.generate_content("Write a story about a magic backpack.")
        print(response.text)

    async def test_chat_enhancement_with_vertex(self):
        logger.debug("test_chat_enhancement_with_vertex")

        REGION = "europe-west9"
        vertexai.init(project=PROJECT_ID, location=REGION)

        model = GenerativeModel("gemini-1.5-flash")

        response = model.generate_content("Write a story about a magic backpack.")
        print(response.text)
