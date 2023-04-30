from django.contrib.auth import get_user_model
from django.test import TestCase

from user.serializers import UserSerializer


class UserApiTests(TestCase):
    def test_create_superuser_and_user(self) -> None:
        admin = get_user_model().objects.create_superuser(
            email="test@gmail.com", password="555qaz", is_staff=True
        )
        user = UserSerializer().create(
            validated_data={
                "email": "test5@gmail.com",
                "password": "555qaz",
                "is_staff": False,
            }
        )

        self.assertTrue(admin.is_superuser)
        self.assertFalse(user.is_staff)

    def test_user_password(self) -> None:
        test_user = get_user_model().objects.create_user(
            email="test@gmail.com", password="test12345", is_staff=False
        )
        UserSerializer(test_user).update(
            test_user, validated_data={"password": "new_password"}
        )

        self.assertEquals(test_user.check_password("new_password"), True)
