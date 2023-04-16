from django.views import View
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request

from borrowing.models import Borrowing


class IsOwnerOrReadOnly(BasePermission):
    """Object-level permission to only allow owners of an object to edit it."""

    def has_object_permission(
        self, request: Request, view: View, obj: Borrowing
    ) -> bool:
        if request.method in SAFE_METHODS:
            return True

        return obj.user == request.user
