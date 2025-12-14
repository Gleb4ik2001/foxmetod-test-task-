from celery import shared_task
import time
import random

from .models import Transaction


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=3,
    retry_kwargs={"max_retries": 3}
)
def send_notification(self, transaction_id):
    time.sleep(5)

    if random.choice([True, False]):
        raise Exception("Telegram API error")

    tx = Transaction.objects.get(id=transaction_id)
    print(f"Notify user {tx.to_wallet.user_id} about +{tx.amount}")
