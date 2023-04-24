from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from user.models import User
from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create new user"""

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Update user witch already login"""

    serializer_class = UserSerializer

    def get_object(self) -> User:
        return self.request.user
