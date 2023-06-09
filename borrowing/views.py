import asyncio
from typing import Type, Optional

import stripe
from django.db.models import QuerySet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status, generics
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from borrowing.models import Borrowing, Payment
from borrowing.pagination import OrderPagination
from borrowing.permissions import IsOwnerOrReadOnly
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
)
from borrowing.telegram_notification import send_message


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BorrowingSerializer
    pagination_class = OrderPagination

    def get_queryset(self) -> QuerySet:
        queryset = Borrowing.objects.select_related("book", "user").prefetch_related(
            "payments"
        )

        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if self.request.user.is_staff:
            if user_id:
                queryset = queryset.filter(user_id=user_id)

            if is_active and is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)

            return queryset

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        return super().get_serializer_class()

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsOwnerOrReadOnly],
        serializer_class=BorrowingReturnSerializer,
    )
    def return_borrowing(self, request: Request, pk: Optional[int] = None) -> Response:
        """Endpoint for returning a borrowed book"""

        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,
        url_path="success",
        permission_classes=[IsOwnerOrReadOnly],
    )
    def borrowing_is_successfully_paid(
        self, request: Request, pk: Optional[int] = None
    ) -> Response:
        """Success endpoint after paying for the borrowing."""

        borrowing = self.get_object()
        session_id = request.query_params.get("session_id")
        payment = Payment.objects.get(session_id=session_id)
        session = stripe.checkout.Session.retrieve(session_id)

        if session["payment_status"] == "paid":
            payment.status = "PAID"
            payment.save()

            message = f"{payment.borrowing.book.title} was paid."
            asyncio.run(send_message(message=message))
            serializer = self.get_serializer(borrowing)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"Fail": "Payment wasn't successful."}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=["GET"],
        detail=True,
        url_path="cancel",
    )
    def borrowing_payment_is_cancelled(
        self, request: Request, pk: Optional[int] = None
    ) -> Response:
        """Cancel endpoint for borrowing payment."""

        borrowing = self.get_object()
        session_id = request.query_params.get("session_id")
        session = stripe.checkout.Session.retrieve(session_id)

        return Response(
            {
                "Cancel": f"The payment for the {borrowing} is cancelled. "
                f"Make sure to pay during 24 hours. Payment url: "
                f"{session.url}. Thanks!"
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.STR,
                description="Filtering by active borrowing (ex. ?is_active=true)",
            ),
            OpenApiParameter(
                "user_id",
                type=OpenApiTypes.NUMBER,
                description="Filtering by specified user (ex. ?user_id=4)",
            ),
        ]
    )
    def list(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user=self.request.user)


class PaymentListView(generics.ListCreateAPIView):
    queryset = Payment.objects.select_related("borrowing__user", "borrowing__book")
    serializer_class = PaymentCreateSerializer
    pagination_class = OrderPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        if self.request.user.is_authenticated:
            return (
                super().get_queryset().filter(borrowing__user_id=self.request.user.id)
            )
        return super().get_queryset()

    def create(
        self, request: Request, *args: tuple, **kwargs: dict
    ) -> Response | ValidationError:
        borrowing_id = request.data["borrowing"]
        borrowing = get_object_or_404(Borrowing, id=borrowing_id)
        borrowing_user = borrowing.user_id

        if request.user.id != borrowing_user:
            raise ValidationError("You cannot pay instead of another user!")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def list(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PaymentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PaymentSerializer(queryset, many=True)
        return Response(serializer.data)


class PaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.select_related("borrowing__user", "borrowing__book")
    serializer_class = PaymentSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        if self.request.user.is_authenticated:
            return (
                super().get_queryset().filter(borrowing__user_id=self.request.user.id)
            )
        return super().get_queryset()
