import datetime

from meertime.settings import env

# Use django-post-office as the email backend
EMAIL_BACKEND = "post_office.EmailBackend"
DEFAULT_FROM_EMAIL = env("EMAIL_FROM", default="noreply@adacs.org.au")
ADMIN_EMAIL = env("ADMIN_EMAIL", default="meertime@astro.swin.edu.au")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT", default=25)

# Configure django-post-office
POST_OFFICE = {
    "MAX_RETRIES": 24 * 4,  # Retry for 24 hours (4 retries per hour)
    "RETRY_INTERVAL": datetime.timedelta(minutes=15),
    "MESSAGE_ID_ENABLED": True,
    "LOG_LEVEL": 2,  # Log both successful and failed deliveries
    "THREADS_PER_PROCESS": 32,
}
