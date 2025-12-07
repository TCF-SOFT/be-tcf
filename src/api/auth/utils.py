from svix import Webhook, exceptions

from utils.logging import logger


def verify_signature(
    payload,
    headers: dict[str, str],
    secret: str,
) -> bool:
    """
    Hash-based Message Authentication Code (HMAC)
    """
    wh = Webhook(secret)
    try:
        wh.verify(payload, headers)
        return True
    except (
        exceptions.WebhookVerificationError,
        exceptions.HTTPValidationError,
        exceptions.HttpError,
    ) as e:
        logger.error("[Webhook] Signature verification failed: %s", str(e))
        return False
