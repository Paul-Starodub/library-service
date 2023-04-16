from datetime import date
from typing import Optional, Type

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from book.models import Book


class Borrowing(models.Model):
    """Borrow model"""

    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="borrowings"
    )

    def validate_return_dates(
        self,
        expected_return_date: str,
        actual_return_date: str,
        error_to_raise: Type[ValidationError],
    ) -> None:
        """Validate that return dates are later than the borrow date at the db level"""

        for return_date_attr in (expected_return_date, actual_return_date):
            return_date_value = getattr(self, str(return_date_attr))

            if return_date_value and return_date_value <= date.today():
                raise error_to_raise(
                    {
                        return_date_attr: "You should take "
                        f"{return_date_attr.replace('_', ' ')} later than "
                        f"borrow date: {date.today()}"
                    }
                )

    def clean(self) -> None:
        self.validate_return_dates(
            "expected_return_date",
            "actual_return_date",
            ValidationError,
        )

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[list[str]] = None,
    ) -> None:
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return f"{self.user}: {self.book.title}"
