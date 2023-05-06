from django.db import models
from django.db.models import CheckConstraint, Q


class Book(models.Model):
    """Book model"""

    class Enum(models.TextChoices):
        HARD = "hard"
        SOFT = "soft"

    title = models.CharField(max_length=63)
    author = models.CharField(max_length=128)
    cover = models.CharField(max_length=4, choices=Enum.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        return self.title

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(daily_fee__gte=0),
                name="daily_fee_gte_0",
                violation_error_message="Borrowing cost cannot be less than zero",
            )
        ]
