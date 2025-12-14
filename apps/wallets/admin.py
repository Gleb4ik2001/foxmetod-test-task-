from django.contrib import admin
from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "balance", "is_system")
    list_filter = ("is_system",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "from_wallet",
        "to_wallet",
        "amount",
        "fee",
        "status",
        "created_at",
    )
    readonly_fields = ("created_at",)
