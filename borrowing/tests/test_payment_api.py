import datetime
from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Payment
from .test_borrowing_api import sample_book, sample_borrowing

PAYMENT_URL = reverse("borrowing:payments-list")


class AuthenticatedPaymentApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.client2 = APIClient()
        self.user = get_user_model().objects.create_user(
            "test1@gmail.com",
            "test_pass",
        )
        self.admin = get_user_model().objects.create_superuser(
            "admin@gmail.com", password="test_pass_admin", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.client2.force_authenticate(self.admin)

    def test_permissions_auth(self) -> None:
        book = sample_book()
        borrowing = sample_borrowing(
            book=book,
            user=self.user,
            actual_return_date=datetime.date.today() + datetime.timedelta(weeks=4),
        )
        Payment.objects.create(
            status="pending",
            type="payment",
            borrowing=borrowing,
            session_url="https://678yugiuf658i",
            session_id=127,
            money_to_pay=book.daily_fee,
        )
        response = self.client.get(PAYMENT_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_queryset_and_str(self) -> None:
        book1 = sample_book()
        book2 = sample_book()
        borrowing1 = sample_borrowing(
            book=book1,
            user=self.user,
            actual_return_date=datetime.date.today() + datetime.timedelta(weeks=4),
        )
        borrowing2 = sample_borrowing(
            book=book2,
            user=self.admin,
            actual_return_date=datetime.date.today() + datetime.timedelta(weeks=4),
        )
        Payment.objects.create(
            status="pending",
            type="payment",
            borrowing=borrowing1,
            session_url="https://678yugiuf658i",
            session_id=127,
            money_to_pay=book1.daily_fee,
        )
        payment2 = Payment.objects.create(
            status="pending",
            type="payment",
            borrowing=borrowing2,
            session_url="https://678yu90giuf658i",
            session_id=128,
            money_to_pay=book2.daily_fee,
        )
        response = self.client2.get(PAYMENT_URL)

        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(str(payment2), "Payment (Interesting book)")
