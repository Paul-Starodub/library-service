import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)

BORROWING_URL = reverse("borrowing:borrowing-list")


def detail_borrowing_url(borrowing_id: int) -> str:
    return reverse("borrowing:borrowing-detail", kwargs={"pk": borrowing_id})


def sample_book(**params: dict) -> Book:
    defaults = {
        "title": "Interesting book",
        "author": "Brown Mister",
        "cover": "hard",
        "inventory": 12,
        "daily_fee": 3.78,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(**params: dict) -> Borrowing:
    defaults = {
        "borrow_date": datetime.date.today(),
        "expected_return_date": datetime.date.today() + datetime.timedelta(weeks=2),
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


class UnAuthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            "test1@gmail.com",
            "test_pass",
        )
        self.client.force_authenticate(self.user1)

    def test_list_borrowings(self) -> None:
        book1 = sample_book()
        book2 = sample_book(title="Very interesting book")
        sample_borrowing(book=book1, user=self.user1)
        sample_borrowing(book=book2, user=self.user1)

        response = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(borrowings), 2)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_borrowing_detail(self) -> None:
        book = sample_book()
        borrowing = sample_borrowing(book=book, user=self.user1)

        url = detail_borrowing_url(borrowing.id)
        response = self.client.get(url)
        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_create_borrowing(self) -> None:
        payload = {
            "expected_return_date": datetime.date.today() + datetime.timedelta(weeks=3),
            "book": sample_book().id,
        }
        response = self.client.post(BORROWING_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_borrowing_not_allowed(self) -> None:
        book = sample_book()
        borrowing = sample_borrowing(book=book, user=self.user1)
        url = detail_borrowing_url(borrowing.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_return_borrowing(self) -> None:
        book = sample_book()
        borrowing = sample_borrowing(
            book=book,
            user=self.user1,
        )

        url = reverse(
            "borrowing:borrowing-return-borrowing", kwargs={"pk": borrowing.id}
        )
        response = self.client.post(
            url,
            data={
                "actual_return_date": datetime.date.today()
                + datetime.timedelta(weeks=4)
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.client2 = APIClient()
        self.client3 = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "test_pass", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.user2 = get_user_model().objects.create_user(
            "user2@user.com", "test_pass2"
        )
        self.client2.force_authenticate(self.user2)
        self.user3 = get_user_model().objects.create_user(
            "user3@user.com", "test_pass3"
        )
        self.client3.force_authenticate(self.user3)

    def test_filter_borrowings_by_is_active(self) -> None:
        book1 = sample_book()
        book2 = sample_book()

        borrowing1 = sample_borrowing(
            book=book1, user=self.user, actual_return_date=None
        )
        borrowing2 = sample_borrowing(
            book=book2,
            user=self.user,
            actual_return_date=datetime.date.today() + datetime.timedelta(weeks=4),
        )

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)

        response = self.client.get(BORROWING_URL, {"is_active": "True"})

        self.assertIn(serializer1.data, response.data["results"])
        self.assertNotIn(serializer2.data, response.data["results"])

    def test_filter_borrowing_by_user_id(self) -> None:
        book1 = sample_book()
        book2 = sample_book()

        sample_borrowing(
            book=book1,
            user=self.user2,
            actual_return_date=datetime.date.today() + datetime.timedelta(weeks=3),
        )
        sample_borrowing(
            book=book2,
            user=self.user3,
            actual_return_date=datetime.date.today() + datetime.timedelta(weeks=4),
        )

        response = self.client.get(BORROWING_URL, {"user_id": 2})

        self.assertEqual(len(Borrowing.objects.all()), 2)
        self.assertEqual(len(Borrowing.objects.filter(user_id=2)), 1)
        self.assertEqual(len(response.data["results"]), 1)
