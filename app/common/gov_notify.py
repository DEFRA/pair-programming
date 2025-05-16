# Gov Notify email utility
from notifications_python_client.notifications import NotificationsAPIClient

from app.config import config

client = NotificationsAPIClient(config.GOV_NOTIFY_API_KEY)


def send_pair_email(to_email: str, pair_name: str, pair_email: str):
    personalisation = {
        "pair_name": pair_name,
        "pair_email": pair_email,
    }
    return client.send_email_notification(
        email_address=to_email,
        template_id=config.GOV_NOTIFY_TEMPLATE_ID,
        personalisation=personalisation,
    )
