from django.contrib import admin

from .models import Booking, LessonSlot

admin.site.register(LessonSlot)
admin.site.register(Booking)
