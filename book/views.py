from rest_framework.viewsets import ModelViewSet

from book.models import Book
from book.permissions import IsAdminOrIfAuthenticatedReadOnly
from book.serializers import BookSerializer


class BookViewSet(ModelViewSet):
    """Book CRUD endpoints"""

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
