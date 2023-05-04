from decimal import Decimal

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")

    @staticmethod
    def validate_daily_fee(value) -> ValidationError | Decimal:
        if value < 0:
            raise serializers.ValidationError(
                "Borrowing cost cannot be less than zero!"
            )
        return value
