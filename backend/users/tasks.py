from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import logging


@shared_task(bind=True, ignore_result=True)
def send_login_otp_email(self, user_id: int, otp_code: str) -> None:
    """
    Send the login OTP email asynchronously.
    Falls back to logging if user cannot be found.
    """
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logging.getLogger(__name__).warning(f"send_login_otp_email: user {user_id} not found")
        return

    try:
        send_mail(
            subject='Your MediSync login verification code',
            message=(
                f'Hello {user.full_name or user.email},\n\n'
                f'Your verification code is: {otp_code}.\n'
                f'This code expires in 5 minutes. If you did not attempt to sign in, you can ignore this email.'
            ),
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        logging.getLogger(__name__).error(f"send_login_otp_email: failed to send email to {user.email}: {e}")