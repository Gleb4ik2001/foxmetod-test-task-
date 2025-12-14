from rest_framework import serializers
import uuid


class TransferSerializer(serializers.Serializer):
    to_user_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    idempotency_key = serializers.UUIDField(default=uuid.uuid4)
