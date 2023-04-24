from django.urls import path, include
from rest_framework import routers

from borrowing.views import BorrowingViewSet, PaymentListView, PaymentDetailView

router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet, basename="borrowing")


urlpatterns = [
    path("", include(router.urls)),
    path("payments/", PaymentListView.as_view(), name="payments-list"),
    path("payments/<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
]
app_name = "borrowing"
