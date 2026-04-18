from datetime import datetime, time, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from booking.models import LessonSlot
from courses.models import Category, Course, Lesson, Module
from learning.models import (
    Enrollment,
    EnrollmentRequest,
    ProgressRecord,
    Quiz,
    QuizChoice,
    QuizQuestion,
    Task,
    TaskSubmission,
)
from users.models import UserProfile


class Command(BaseCommand):
    help = "Create demo accounts, courses, lessons, activities, and slots for the V1 defense demo."

    def handle(self, *args, **options):
        teacher, _ = User.objects.get_or_create(
            username="demo_teacher",
            defaults={"email": "teacher@example.com"},
        )
        teacher.set_password("TeacherPass123")
        teacher.save()
        profile, _ = UserProfile.objects.get_or_create(user=teacher)
        profile.role = UserProfile.Role.TEACHER
        profile.bio = "Demo English teacher for the V1 catalog."
        profile.save(update_fields=["role", "bio"])

        student, _ = User.objects.get_or_create(
            username="demo_student",
            defaults={"email": "student@example.com"},
        )
        student.set_password("StudentPass123")
        student.save()
        student_profile, _ = UserProfile.objects.get_or_create(user=student)
        student_profile.role = UserProfile.Role.STUDENT
        student_profile.bio = "Demo student account for showing enrollment, lessons, progress, tasks, and booking."
        student_profile.save(update_fields=["role", "bio"])

        categories = {
            "Speaking": "Courses focused on confidence, pronunciation, and real conversations.",
            "Grammar": "Courses focused on sentence structure and correct English usage.",
            "Exam Prep": "Courses for IELTS-style reading, listening, writing, and speaking practice.",
        }

        category_objects = {}
        for name, description in categories.items():
            category_objects[name], _ = Category.objects.update_or_create(
                name=name,
                defaults={"description": description},
            )

        demo_courses = [
            {
                "title": "Everyday English Speaking",
                "description": "Learn practical phrases for introductions, daily routines, and simple conversations.",
                "level": "A1-A2",
                "category": "Speaking",
                "image_url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
                "modules": [
                    {
                        "title": "Meeting People",
                        "lessons": [
                            {
                                "title": "Greetings and Introductions",
                                "youtube_url": "https://www.youtube.com/watch?v=HAnw168huqA",
                                "content": "Practice basic greetings, names, and polite introductions.",
                                "quiz": {
                                    "title": "Greetings Check",
                                    "questions": [
                                        {
                                            "text": "Which phrase is a polite greeting?",
                                            "choices": [
                                                ("Good morning", True),
                                                ("Go away", False),
                                                ("I am hungry", False),
                                            ],
                                        },
                                        {
                                            "text": "Which answer fits: 'Nice to meet you'?",
                                            "choices": [
                                                ("Nice to meet you too", True),
                                                ("Yesterday", False),
                                                ("At the station", False),
                                            ],
                                        },
                                    ],
                                },
                                "task": {
                                    "title": "Write a short introduction",
                                    "instructions": "Write 3-4 sentences introducing yourself, your city, and one hobby.",
                                },
                            },
                            {
                                "title": "Talking About Yourself",
                                "youtube_url": "https://www.youtube.com/watch?v=CVD5w6PJn18",
                                "content": "Learn simple sentences about your city, study, work, and hobbies.",
                                "quiz": {
                                    "title": "About Yourself Check",
                                    "questions": [
                                        {
                                            "text": "Choose the best sentence.",
                                            "choices": [
                                                ("I am from Almaty.", True),
                                                ("I from Almaty.", False),
                                                ("I Almaty from.", False),
                                            ],
                                        }
                                    ],
                                },
                                "task": {
                                    "title": "Personal profile answer",
                                    "instructions": "Write a short answer to: Where are you from and what do you like doing?",
                                },
                            },
                        ],
                    },
                    {
                        "title": "Daily Conversations",
                        "lessons": [
                            {
                                "title": "Ordering Food",
                                "youtube_url": "https://www.youtube.com/watch?v=bgfdqVmVjfk",
                                "content": "Use polite phrases for cafes and restaurants.",
                            },
                            {
                                "title": "Asking for Directions",
                                "youtube_url": "https://www.youtube.com/watch?v=DPYJQSA-x50",
                                "content": "Practice questions and answers for finding places.",
                            },
                        ],
                    },
                ],
            },
            {
                "title": "Grammar Foundations",
                "description": "Understand the grammar needed to build clear English sentences.",
                "level": "A2-B1",
                "category": "Grammar",
                "image_url": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8",
                "modules": [
                    {
                        "title": "Present Tenses",
                        "lessons": [
                            {
                                "title": "Present Simple",
                                "youtube_url": "https://www.youtube.com/watch?v=L9AWrJnhsRI",
                                "content": "Learn how to describe habits, facts, and routines.",
                            },
                            {
                                "title": "Present Continuous",
                                "youtube_url": "https://www.youtube.com/watch?v=Dl8g2pZ82ME",
                                "content": "Learn how to talk about actions happening now.",
                            },
                        ],
                    },
                    {
                        "title": "Past Tenses",
                        "lessons": [
                            {
                                "title": "Past Simple Regular Verbs",
                                "youtube_url": "https://www.youtube.com/watch?v=QlZXd-m6Pdw",
                                "content": "Practice regular past tense forms and common time markers.",
                            },
                            {
                                "title": "Past Simple Irregular Verbs",
                                "youtube_url": "https://www.youtube.com/watch?v=MA3NFtLc22k",
                                "content": "Learn common irregular verbs for everyday stories.",
                            },
                        ],
                    },
                ],
            },
            {
                "title": "IELTS Speaking Starter",
                "description": "Prepare basic answers for IELTS Speaking Part 1 and improve fluency.",
                "level": "B1-B2",
                "category": "Exam Prep",
                "image_url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173",
                "modules": [
                    {
                        "title": "Speaking Part 1",
                        "lessons": [
                            {
                                "title": "Answering Personal Questions",
                                "youtube_url": "https://www.youtube.com/watch?v=qXPSgMo0C1w",
                                "content": "Build short, natural answers about home, study, work, and hobbies.",
                            },
                            {
                                "title": "Extending Your Answers",
                                "youtube_url": "https://www.youtube.com/watch?v=QGdUe3pG6jA",
                                "content": "Use reasons and examples to make answers stronger.",
                            },
                        ],
                    },
                    {
                        "title": "Fluency Practice",
                        "lessons": [
                            {
                                "title": "Avoiding Long Pauses",
                                "youtube_url": "https://www.youtube.com/watch?v=ZnZElENi5W8",
                                "content": "Use simple linking phrases while thinking.",
                            },
                            {
                                "title": "Clear Pronunciation Basics",
                                "youtube_url": "https://www.youtube.com/watch?v=htmkbIboG9Q",
                                "content": "Practice stress, rhythm, and clear final sounds.",
                            },
                        ],
                    },
                ],
            },
        ]

        for course_index, course_data in enumerate(demo_courses, start=1):
            course, _ = Course.objects.update_or_create(
                title=course_data["title"],
                defaults={
                    "category": category_objects[course_data["category"]],
                    "description": course_data["description"],
                    "level": course_data["level"],
                    "image_url": course_data["image_url"],
                    "teacher": teacher,
                    "is_published": True,
                },
            )

            for module_index, module_data in enumerate(course_data["modules"], start=1):
                module, _ = Module.objects.update_or_create(
                    course=course,
                    title=module_data["title"],
                    defaults={"order": module_index},
                )

                for lesson_index, lesson_data in enumerate(module_data["lessons"], start=1):
                    Lesson.objects.update_or_create(
                        module=module,
                        title=lesson_data["title"],
                        defaults={
                            "youtube_url": lesson_data["youtube_url"],
                            "content": lesson_data["content"],
                            "order": lesson_index,
                        },
                    )
                    lesson = Lesson.objects.get(module=module, title=lesson_data["title"])

                    quiz_data = lesson_data.get("quiz")
                    if quiz_data:
                        quiz, _ = Quiz.objects.update_or_create(
                            lesson=lesson,
                            defaults={"title": quiz_data["title"]},
                        )
                        for question_index, question_data in enumerate(quiz_data["questions"], start=1):
                            question, _ = QuizQuestion.objects.update_or_create(
                                quiz=quiz,
                                text=question_data["text"],
                                defaults={"order": question_index},
                            )
                            for choice_index, (choice_text, is_correct) in enumerate(question_data["choices"], start=1):
                                QuizChoice.objects.update_or_create(
                                    question=question,
                                    text=choice_text,
                                    defaults={
                                        "is_correct": is_correct,
                                        "order": choice_index,
                                    },
                                )

                    task_data = lesson_data.get("task")
                    if task_data:
                        Task.objects.update_or_create(
                            lesson=lesson,
                            title=task_data["title"],
                            defaults={"instructions": task_data["instructions"]},
                        )

            self.stdout.write(self.style.SUCCESS(f"Seeded course {course_index}: {course.title}"))

        starter_course = Course.objects.get(title="Everyday English Speaking")
        Enrollment.objects.get_or_create(student=student, course=starter_course)
        EnrollmentRequest.objects.update_or_create(
            student=student,
            course=starter_course,
            defaults={"status": EnrollmentRequest.Status.APPROVED},
        )
        first_lesson = Lesson.objects.get(module__course=starter_course, title="Greetings and Introductions")
        ProgressRecord.objects.update_or_create(
            student=student,
            lesson=first_lesson,
            defaults={"is_completed": True},
        )

        first_task = Task.objects.filter(lesson=first_lesson).first()
        if first_task:
            TaskSubmission.objects.update_or_create(
                student=student,
                task=first_task,
                defaults={
                    "answer_text": "Hello! My name is Demo Student. I live in Almaty. I like learning English and practicing speaking.",
                    "status": TaskSubmission.Status.SUBMITTED,
                    "score": None,
                },
            )

        LessonSlot.objects.filter(teacher=teacher, booking__isnull=True).delete()
        start_date = timezone.localdate() + timedelta(days=1)
        start_time = timezone.make_aware(datetime.combine(start_date, time(hour=10)))
        for slot_index in range(3):
            starts_at = start_time + timedelta(days=slot_index)
            slot, _ = LessonSlot.objects.update_or_create(
                teacher=teacher,
                starts_at=starts_at,
                defaults={
                    "ends_at": starts_at + timedelta(minutes=45),
                    "meeting_url": "https://meet.google.com/demo-english-v1",
                    "is_available": True,
                },
            )
            if hasattr(slot, "booking"):
                slot.is_available = False
                slot.save(update_fields=["is_available"])

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write(self.style.SUCCESS("Teacher login: demo_teacher / TeacherPass123"))
        self.stdout.write(self.style.SUCCESS("Student login: demo_student / StudentPass123"))
