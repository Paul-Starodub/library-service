from django.db import models


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
