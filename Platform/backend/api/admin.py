from django.contrib import admin
from .models import Profile, Category, Course, Enrollment, Task, Submission

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Task)
admin.site.register(Submission)