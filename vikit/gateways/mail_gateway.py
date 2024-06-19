import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
from loguru import logger

from vikit.common.config import get_videho_email_contact
from vikit.common.secret import get_sendinblue_api_key


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
