from django.db.models import QuerySet
from rest_framework.generics import GenericAPIView

from borrowing.models import Payment


class CustomQuerySet(GenericAPIView):
    def get_queryset(self) -> QuerySet[Payment]:
        # Get payments only for the authenticated user, or all payments for superuser

        queryset = Payment.objects.all()

        if self.request.user.is_staff:
            return queryset
        elif self.request.user.is_authenticated:
            return queryset.filter(borrowing__user_id=self.request.user.id)
