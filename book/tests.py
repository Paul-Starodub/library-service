from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book

BOOKS_URL = reverse("library:book-list")


class UnAuthenticatedBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        response = self.client.get(BOOKS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_str_method(self) -> None:
        book = Book.objects.create(
            title="Lion", author="Dad", cover="hard", inventory=12, daily_fee=12.08
        )

        self.assertEqual(str(book), "Lion")
