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

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
from loguru import logger

from vikit.common.config import get_videho_email_contact
from vikit.common.secrets import get_sendinblue_api_key


def send_email(emailToSend, nameOfFile):
    """
    Send email to the user with the link to download the video

    Args:
        emailToSend: the email to send the video to
        nameOfFile: the name of the video file to send
    """
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = get_sendinblue_api_key()

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )
    subject = "Videho.ai - Your AI generated video"
    html_content = (
        "<html><body><h1>Your AI Generated video is ready</h1><h3>You can download it here : <a href='https://storage.cloud.google.com/aivideoscreated/"
        + nameOfFile
        + "'>You can download it here</a></h3><br><h4>Thank you for using <a href='https://videho.ai'>Videho.ai</a> !</h4><br></body></html>"
    )

    sender = {"name": "AI generated video", "email": get_videho_email_contact()}
    to = [{"email": emailToSend}]

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to, html_content=html_content, sender=sender, subject=subject
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"api_response {pprint(api_response)}")
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
