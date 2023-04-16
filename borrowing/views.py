from typing import Type, Optional

from django.db.models import QuerySet
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from borrowing.models import Borrowing
from borrowing.permissions import IsOwnerOrReadOnly
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        queryset = Borrowing.objects.select_related("book", "user")

        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if self.request.user.is_staff:
            if user_id:
                queryset = queryset.filter(user_id=user_id)

            if is_active:
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

        if self.action == "return_borrowing":
            return BorrowingReturnSerializer

        return self.serializer_class

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsOwnerOrReadOnly],
    )
    def return_borrowing(self, request: Request, pk: Optional[int] = None) -> Response:
        """Endpoint for returning a borrowed book"""

        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user=self.request.user)
