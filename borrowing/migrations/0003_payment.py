# Generated by Django 4.2 on 2023-04-23 11:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("borrowing", "0002_alter_borrowing_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("paid", "Paid")],
                        default="pending",
                        max_length=7,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("payment", "Payment"), ("fine", "Fine")], max_length=7
                    ),
                ),
                ("session_url", models.URLField(max_length=250)),
                ("session_id", models.CharField(max_length=250)),
                (
                    "money_to_pay",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "borrowing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="borrowing.borrowing",
                    ),
                ),
            ],
        ),
    ]