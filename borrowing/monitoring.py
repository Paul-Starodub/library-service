import datetime

from book.models import Book
from borrowing.models import Borrowing
from user.models import User


def filtering_borrowing():
    """Filtering data"""

    permission_date = datetime.date.today() + datetime.timedelta(days=1)
    expired_borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True, expected_return_date__lte=permission_date
    ).select_related("book", "user")

    if expired_borrowings:
        message = ""

        for borrowing in expired_borrowings:
            message += (
                f"Book '{Book.objects.get(id=borrowing.book_id)}' was borrowed by user"
                f" {User.objects.get(id=borrowing.user_id)} at "
                f"{borrowing.borrow_date}. The book must be returned "
                f"{borrowing.expected_return_date}\n"
            )

    else:
        message = "No borrowings overdue today!"
    return message
