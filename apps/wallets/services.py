from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Wallet, Transaction, TransactionStatus


COMMISSION_THRESHOLD = Decimal("1000.00")
COMMISSION_RATE = Decimal("0.10")


def transfer_funds(
    *,
    from_user,
    to_user,
    amount,
    idempotency_key
):
    with transaction.atomic():

        if Transaction.objects.filter(idempotency_key=idempotency_key).exists():
            raise ValidationError("Duplicate request")

        from_wallet = (
            Wallet.objects
            .select_for_update()
            .get(user=from_user)
        )
        to_wallet = (
            Wallet.objects
            .select_for_update()
            .get(user=to_user)
        )
        admin_wallet = (
            Wallet.objects
            .select_for_update()
            .get(is_system=True)
        )

        fee = Decimal("0.00")
        total = amount

        if amount > COMMISSION_THRESHOLD:
            fee = amount * COMMISSION_RATE
            total += fee

        if from_wallet.balance < total:
            raise ValidationError("Недостаточно средств")

        tx = Transaction.objects.create(
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount=amount,
            fee=fee,
            idempotency_key=idempotency_key,
            status=TransactionStatus.PENDING
        )

        from_wallet.balance -= total
        to_wallet.balance += amount
        admin_wallet.balance += fee

        from_wallet.save()
        to_wallet.save()
        admin_wallet.save()

        tx.status = TransactionStatus.SUCCESS
        tx.save(update_fields=["status"])

        return tx
