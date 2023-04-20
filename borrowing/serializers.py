import datetime

from django.db import transaction
from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing
from borrowing.telegram_notification import borrowing_telegram_notification
from user.serializers import UserSerializer


def validate_date(attrs: dict, date: str) -> dict:
    """Checking the correctness of the date at the api level"""

    if attrs[date] is None:
        raise serializers.ValidationError("You need to enter a date.")

    if attrs[date] <= datetime.date.today():
        raise serializers.ValidationError(
            f"You should take expected return date later than {datetime.date.today()}."
        )

    return attrs


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.SlugRelatedField(many=False, read_only=True, slug_field="title")
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")


class BorrowingCreateSerializer(BorrowingSerializer):
    def validate(self, attrs: dict) -> dict:
        return validate_date(attrs=attrs, date="expected_return_date")

    @transaction.atomic()
    def create(self, validated_data: dict) -> Borrowing:
        book_borrowing = validated_data.get("book")

        if book_borrowing.inventory == 0:
            raise serializers.ValidationError("This book is currently out of stock.")

        book_borrowing.inventory -= 1
        book_borrowing.save()
        message = (
            f"{book_borrowing} was borrowed by the user "
            f"{validated_data.get('user')}. Expected return date {validated_data.get('expected_return_date')}"
        )
        borrowing_telegram_notification(message=message)

        return super().create(validated_data)

    class Meta:
        model = Borrowing
        fields = ("expected_return_date", "book")


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)


class BorrowingReturnSerializer(BorrowingSerializer):
    def validate(self, attrs: dict) -> dict:
        return validate_date(attrs=attrs, date="actual_return_date")

    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")

    @transaction.atomic()
    def update(self, instance: Borrowing, validated_data: dict) -> Borrowing:
        if instance.actual_return_date is not None:
            raise serializers.ValidationError(
                "It is not possible to donate the same book twice."
            )

        instance.book.inventory += 1
        instance.book.save()

        borrowing = super().update(instance, validated_data)
        return borrowing
