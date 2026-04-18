from django.contrib import admin

from .models import (
    Enrollment,
    ProgressRecord,
    Quiz,
    QuizChoice,
    QuizQuestion,
    QuizSubmission,
    Task,
    TaskSubmission,
)

admin.site.register(Enrollment)
admin.site.register(Task)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
admin.site.register(QuizChoice)
admin.site.register(QuizSubmission)
admin.site.register(TaskSubmission)
admin.site.register(ProgressRecord)
