from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .serializers import TransferSerializer
from .services import transfer_funds
from .tasks import send_notification


User = get_user_model()


class TransferAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            to_user = User.objects.get(
                id=serializer.validated_data["to_user_id"]
            )

            tx = transfer_funds(
                from_user=request.user,
                to_user=to_user,
                amount=serializer.validated_data["amount"],
                idempotency_key=serializer.validated_data["idempotency_key"]
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Recipient not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        send_notification.delay(tx.id)

        return Response(
            {
                "transaction_id": tx.id,
                "status": tx.status,
            },
            status=status.HTTP_201_CREATED
        )
