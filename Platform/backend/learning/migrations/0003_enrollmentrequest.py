from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_approved_requests_for_existing_enrollments(apps, schema_editor):
    Enrollment = apps.get_model("learning", "Enrollment")
    EnrollmentRequest = apps.get_model("learning", "EnrollmentRequest")

    for enrollment in Enrollment.objects.all():
        EnrollmentRequest.objects.get_or_create(
            student_id=enrollment.student_id,
            course_id=enrollment.course_id,
            defaults={
                "status": "approved",
                "created_at": enrollment.created_at,
                "updated_at": enrollment.created_at,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("courses", "0002_category_course_image_url_course_category"),
        ("learning", "0002_quiz_quizquestion_quizchoice_quizsubmission_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EnrollmentRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "course",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="courses.course"),
                ),
                (
                    "student",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
                "unique_together": {("student", "course")},
            },
        ),
        migrations.RunPython(create_approved_requests_for_existing_enrollments, migrations.RunPython.noop),
    ]
