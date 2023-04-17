from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


BOOKS_URL = reverse("library:book-list")


class UnAuthenticatedBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        response = self.client.get(BOOKS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
