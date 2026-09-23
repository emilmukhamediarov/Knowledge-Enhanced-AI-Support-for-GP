import boto3
from botocore.exceptions import BotoCoreError, ClientError
from app.config import (
    AWS_PROFILE,
    AWS_REGION,
    SES_FROM_EMAIL,
)

class EmailDeliveryError(RuntimeError):
    pass

#Connect to AWS SES and return the client
def _get_ses_client():
    session_options = {
        "region_name": AWS_REGION,
    }
    if AWS_PROFILE:
        session_options["profile_name"] = AWS_PROFILE
    session = boto3.Session(**session_options)
    return session.client("sesv2")


def send_verification_email(
    recipient_email: str,
    verification_code: str,
) -> str:
    
    if not SES_FROM_EMAIL:
        raise EmailDeliveryError(
            "SES_FROM_EMAIL is not configured"
        )

    client = _get_ses_client()

    subject = "Your MidBit verification code"
    text_body = (
        f"Your MidBit verification code is: "
        f"{verification_code}\n\n"
        "This code will expire in 10 minutes. "
        "If you did not request this code, you can ignore this email. "
        "Due to tight funds, we will charge 10USD to each user who requests a verification code."
    )

    try:
        response = client.send_email(
            FromEmailAddress=SES_FROM_EMAIL,
            Destination={
                "ToAddresses": [recipient_email],
            },
            Content={
                "Simple": {
                    "Subject": {
                        "Data": subject,
                        "Charset": "UTF-8",
                    },
                    "Body": {
                        "Text": {
                            "Data": text_body,
                            "Charset": "UTF-8",
                        },
                    },
                },
            },
        )
    except (ClientError, BotoCoreError) as exc:
        raise EmailDeliveryError(
            "Amazon SES could not send the verification email"
        ) from exc

    return response["MessageId"]