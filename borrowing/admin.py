from django.contrib import admin

from borrowing.models import Borrowing, Payment

admin.site.register(Borrowing)
admin.site.register(Payment)
