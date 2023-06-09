import time
from datetime import date
from typing import Tuple, Optional

import stripe
from django.conf import settings
from rest_framework.exceptions import ValidationError
from borrowing.models import Borrowing

stripe.api_key = settings.STRIPE_SECRET_KEY
FINE_MULTIPLIER = 2  # fine coefficient for overdue days


def create_stripe_session(
    borrowing: Borrowing, act_ret_date: Optional[date] = None
) -> Tuple[str, str] | ValidationError:
    if stripe.api_key:
        expiration_time = int(time.time()) + (
            30 * 60
        )  # Set expiration time to 30 minutes from now

        to_pay = (
            borrowing.expected_return_date - borrowing.borrow_date
        ).days * borrowing.book.daily_fee

        if act_ret_date is not None and act_ret_date > borrowing.expected_return_date:
            count_fine_days = (act_ret_date - borrowing.expected_return_date).days
            to_pay = FINE_MULTIPLIER * count_fine_days * borrowing.book.daily_fee

        correct_url = "http://0.0.0.0:8000/api/library/borrowings/" + str(borrowing.id)

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(to_pay * 100),
                        "product_data": {
                            "name": borrowing.book.title,
                            "description": "Book borrowing fee",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=correct_url + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=correct_url + "/cancel?session_id={CHECKOUT_SESSION_ID}",
            expires_at=expiration_time,
        )
        return checkout_session.url, checkout_session.id

    return ValidationError("Stripe is unavailable, please provide us Stripe creds.")
