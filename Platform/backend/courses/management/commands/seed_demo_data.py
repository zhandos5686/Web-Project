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
    QuizSubmission,
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
                                "quiz": {
                                    "title": "Cafe Conversation Check",
                                    "questions": [
                                        {
                                            "text": "Which phrase is polite when ordering?",
                                            "choices": [
                                                ("Could I have a coffee, please?", True),
                                                ("Give coffee now.", False),
                                                ("Coffee yesterday.", False),
                                            ],
                                        },
                                        {
                                            "text": "Which question asks about the price?",
                                            "choices": [
                                                ("How much is it?", True),
                                                ("Where are you from?", False),
                                                ("What time do you sleep?", False),
                                            ],
                                        },
                                    ],
                                },
                                "task": {
                                    "title": "Cafe role-play lines",
                                    "instructions": "Write a short cafe dialogue with a greeting, an order, and a thank-you phrase.",
                                },
                            },
                            {
                                "title": "Asking for Directions",
                                "youtube_url": "https://www.youtube.com/watch?v=DPYJQSA-x50",
                                "content": "Practice questions and answers for finding places.",
                                "quiz": {
                                    "title": "Directions Language Check",
                                    "questions": [
                                        {
                                            "text": "Which question politely asks for directions?",
                                            "choices": [
                                                ("Excuse me, how can I get to the station?", True),
                                                ("Station go where?", False),
                                                ("I am station.", False),
                                            ],
                                        },
                                        {
                                            "text": "Which phrase means continue walking?",
                                            "choices": [
                                                ("Go straight ahead", True),
                                                ("Sit down here", False),
                                                ("Close the door", False),
                                            ],
                                        },
                                    ],
                                },
                                "task": {
                                    "title": "Directions practice",
                                    "instructions": "Write 4-5 sentences asking for directions to a library, station, or cafe.",
                                },
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
                                "quiz": {
                                    "title": "Present Simple Routine Check",
                                    "questions": [
                                        {
                                            "text": "Choose the correct Present Simple sentence.",
                                            "choices": [
                                                ("She studies English every day.", True),
                                                ("She study English every day.", False),
                                                ("She studying English every day.", False),
                                            ],
                                        },
                                        {
                                            "text": "Which time phrase usually fits Present Simple?",
                                            "choices": [
                                                ("Every morning", True),
                                                ("Right now", False),
                                                ("At the moment", False),
                                            ],
                                        },
                                    ],
                                },
                                "task": {
                                    "title": "Daily routine paragraph",
                                    "instructions": "Write 4-5 sentences about your daily routine using Present Simple.",
                                },
                            },
                            {
                                "title": "Present Continuous",
                                "youtube_url": "https://www.youtube.com/watch?v=Dl8g2pZ82ME",
                                "content": "Learn how to talk about actions happening now.",
                                "quiz": {
                                    "title": "Present Continuous Check",
                                    "questions": [
                                        {
                                            "text": "Choose the correct sentence for an action happening now.",
                                            "choices": [
                                                ("I am reading a book now.", True),
                                                ("I read a book now.", False),
                                                ("I reads a book now.", False),
                                            ],
                                        },
                                        {
                                            "text": "Which phrase often signals Present Continuous?",
                                            "choices": [
                                                ("At the moment", True),
                                                ("Every week", False),
                                                ("Usually", False),
                                            ],
                                        },
                                    ],
                                },
                                "task": {
                                    "title": "What is happening now",
                                    "instructions": "Write 4-5 sentences about what people around you are doing now. Use Present Continuous.",
                                },
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
                                "quiz": {
                                    "title": "Regular Past Verbs Check",
                                    "questions": [
                                        {
                                            "text": "Choose the correct Past Simple form.",
                                            "choices": [
                                                ("I watched a film yesterday.", True),
                                                ("I watch a film yesterday.", False),
                                                ("I watching a film yesterday.", False),
                                            ],
                                        },
                                        {
                                            "text": "Which verb is a regular past form?",
                                            "choices": [
                                                ("played", True),
                                                ("went", False),
                                                ("saw", False),
                                            ],
                                        },
                                    ],
                                },
                                "task": {
                                    "title": "Regular past tense practice",
                                    "instructions": "Write 4-5 sentences about last weekend using regular past tense verbs such as watched, played, visited, or studied.",
                                },
                            },
                            {
                                "title": "Past Simple Irregular Verbs",
                                "youtube_url": "https://www.youtube.com/watch?v=MA3NFtLc22k",
                                "content": "Learn common irregular verbs for everyday stories.",
                                "quiz": {
                                    "title": "Irregular Past Verbs Check",
                                    "questions": [
                                        {
                                            "text": "Choose the correct Past Simple sentence.",
                                            "choices": [
                                                ("We went to the park yesterday.", True),
                                                ("We goed to the park yesterday.", False),
                                                ("We go to the park yesterday.", False),
                                            ],
                                        },
                                        {
                                            "text": "What is the Past Simple of 'buy'?",
                                            "choices": [
                                                ("bought", True),
                                                ("buyed", False),
                                                ("buying", False),
                                            ],
                                        },
                                    ],
                                },
                                "task": {
                                    "title": "Yesterday story",
                                    "instructions": "Write 4-5 sentences about what you did yesterday. Use at least two irregular verbs.",
                                },
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
                                "quiz": {
                                    "title": "IELTS Part 1 Answer Style",
                                    "questions": [
                                        {
                                            "text": "Which answer is best for IELTS Speaking Part 1?",
                                            "choices": [
                                                ("I live in Almaty, a busy city with beautiful mountains nearby.", True),
                                                ("Almaty.", False),
                                                ("Yes, I do.", False),
                                            ],
                                        },
                                        {
                                            "text": "What should a good Part 1 answer usually include?",
                                            "choices": [
                                                ("A direct answer plus a short detail", True),
                                                ("Only one word", False),
                                                ("A memorized essay paragraph", False),
                                            ],
                                        },
                                    ],
                                },
                                "task": {
                                    "title": "Personal IELTS Part 1 answers",
                                    "instructions": "Write sample IELTS Part 1 answers about your hometown, studies, and hobbies. Use 2-3 sentences for each answer.",
                                },
                            },
                            {
                                "title": "Extending Your Answers",
                                "youtube_url": "https://www.youtube.com/watch?v=QGdUe3pG6jA",
                                "content": "Use reasons and examples to make answers stronger.",
                                "quiz": {
                                    "title": "Extending Answers Check",
                                    "questions": [
                                        {
                                            "text": "Which answer is more natural and extended?",
                                            "choices": [
                                                ("I enjoy reading because it helps me relax after classes.", True),
                                                ("Reading.", False),
                                                ("I am reading yesterday.", False),
                                            ],
                                        }
                                    ],
                                },
                                "task": {
                                    "title": "Extended IELTS answers",
                                    "instructions": "Write three IELTS Part 1 answers. Each answer should include a direct answer, one reason, and one example.",
                                },
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
                                "quiz": {
                                    "title": "Fluency Phrase Check",
                                    "questions": [
                                        {
                                            "text": "Which phrase can help you avoid a long silent pause?",
                                            "choices": [
                                                ("Let me think for a moment.", True),
                                                ("I no words.", False),
                                                ("Stop speaking now.", False),
                                            ],
                                        },
                                        {
                                            "text": "Which phrase introduces an example naturally?",
                                            "choices": [
                                                ("For example,", True),
                                                ("Because example yes", False),
                                                ("Never mind", False),
                                            ],
                                        },
                                    ],
                                },
                                "task": {
                                    "title": "Fluency linking practice",
                                    "instructions": "Write five short answers using linking phrases such as 'I think', 'for example', and 'because'.",
                                },
                            },
                            {
                                "title": "Clear Pronunciation Basics",
                                "youtube_url": "https://www.youtube.com/watch?v=htmkbIboG9Q",
                                "content": "Practice stress, rhythm, and clear final sounds.",
                                "quiz": {
                                    "title": "Pronunciation Awareness Check",
                                    "questions": [
                                        {
                                            "text": "What helps make speech clearer?",
                                            "choices": [
                                                ("Speaking with clear word stress and final sounds", True),
                                                ("Speaking as fast as possible", False),
                                                ("Skipping difficult words every time", False),
                                            ],
                                        }
                                    ],
                                },
                                "task": {
                                    "title": "Pronunciation self-check",
                                    "instructions": "Write a short speaking practice plan with three words you want to pronounce clearly and one sentence for each word.",
                                },
                            },
                        ],
                    },
                ],
            },
            {
                "title": "IELTS Essay Writing Mastery",
                "legacy_titles": ["IELTS Essay Writing Master"],
                "description": "Learn how to plan and write clear IELTS Task 2 essays with introductions, body paragraphs, and conclusions.",
                "level": "B1-B2",
                "category": "Exam Prep",
                "image_url": "https://images.unsplash.com/photo-1455390582262-044cdead277a",
                "modules": [
                    {
                        "title": "Essay Structure Basics",
                        "lessons": [
                            {
                                "title": "Understanding IELTS Task 2 Structure",
                                "youtube_url": "https://www.youtube.com/watch?v=1W9iimRFmF0",
                                "content": "Learn the basic structure of an IELTS Task 2 essay: introduction, body paragraphs, and conclusion.",
                                "quiz": {
                                    "title": "Essay Structure Check",
                                    "questions": [
                                        {
                                            "text": "What is the usual structure of an IELTS Task 2 essay?",
                                            "choices": [
                                                ("Introduction, body paragraphs, conclusion", True),
                                                ("Only one long paragraph", False),
                                                ("Questions and short answers only", False),
                                            ],
                                        },
                                        {
                                            "text": "What should a body paragraph usually include?",
                                            "choices": [
                                                ("Main idea, reason, example", True),
                                                ("Only a copied question", False),
                                                ("Only the final opinion", False),
                                            ],
                                        },
                                    ],
                                },
                                "task": {
                                    "title": "Essay plan outline",
                                    "instructions": "Write a simple IELTS Task 2 essay outline with an introduction idea, two body paragraph ideas, and a conclusion idea.",
                                },
                            },
                            {
                                "title": "Writing Strong Introductions",
                                "youtube_url": "https://www.youtube.com/watch?v=YngqHl_BLOU",
                                "content": "Practice paraphrasing the question and writing a clear thesis statement.",
                                "quiz": {
                                    "title": "Introduction and Thesis Check",
                                    "questions": [
                                        {
                                            "text": "Which sentence is a clear thesis statement?",
                                            "choices": [
                                                ("I believe governments should invest more in public transport because it reduces traffic.", True),
                                                ("This essay is about transport.", False),
                                                ("Many people in the world.", False),
                                            ],
                                        },
                                        {
                                            "text": "What is paraphrasing in an IELTS introduction?",
                                            "choices": [
                                                ("Writing the question idea in your own words", True),
                                                ("Copying every word from the question", False),
                                                ("Writing an unrelated story", False),
                                            ],
                                        },
                                    ],
                                },
                                "task": {
                                    "title": "Write an IELTS introduction",
                                    "instructions": "Write a short introduction for this topic: Some people think online learning is better than classroom learning. To what extent do you agree?",
                                },
                            },
                        ],
                    },
                    {
                        "title": "Developing Ideas",
                        "lessons": [
                            {
                                "title": "Opinion Body Paragraphs",
                                "youtube_url": "https://www.youtube.com/watch?v=Y5cZ6nGWqAA",
                                "content": "Learn how to write one clear body paragraph with an opinion, reason, and example.",
                                "quiz": {
                                    "title": "Body Paragraph Check",
                                    "questions": [
                                        {
                                            "text": "Which sentence gives a clear supporting reason?",
                                            "choices": [
                                                ("This is because online courses allow students to review lessons many times.", True),
                                                ("Education is education.", False),
                                                ("I will write about this topic.", False),
                                            ],
                                        },
                                        {
                                            "text": "Which sentence is a useful example?",
                                            "choices": [
                                                ("For example, a student can replay a grammar lesson before an exam.", True),
                                                ("Examples are important.", False),
                                                ("In conclusion, I agree.", False),
                                            ],
                                        },
                                    ],
                                },
                                "task": {
                                    "title": "Write one body paragraph",
                                    "instructions": "Write one body paragraph about online learning. Include your opinion, one reason, and one example.",
                                },
                            },
                            {
                                "title": "Writing Clear Conclusions",
                                "youtube_url": "https://www.youtube.com/watch?v=Zx-JcXsbUqQ",
                                "content": "Practice summarizing your opinion without adding a new main idea.",
                                "quiz": {
                                    "title": "Conclusion Check",
                                    "questions": [
                                        {
                                            "text": "What should a conclusion usually do?",
                                            "choices": [
                                                ("Summarize the main opinion clearly", True),
                                                ("Introduce a completely new topic", False),
                                                ("Copy the whole introduction", False),
                                            ],
                                        }
                                    ],
                                },
                                "task": {
                                    "title": "Write a conclusion",
                                    "instructions": "Write a 2-sentence conclusion for an essay about whether students should study online or in classrooms.",
                                },
                            },
                        ],
                    },
                ],
            },
        ]

        for course_index, course_data in enumerate(demo_courses, start=1):
            course_defaults = {
                "title": course_data["title"],
                "category": category_objects[course_data["category"]],
                "description": course_data["description"],
                "level": course_data["level"],
                "image_url": course_data["image_url"],
                "teacher": teacher,
                "is_published": True,
            }
            course = Course.objects.filter(title=course_data["title"]).first()
            if course is None:
                course = Course.objects.filter(title__in=course_data.get("legacy_titles", [])).first()
            if course:
                for field, value in course_defaults.items():
                    setattr(course, field, value)
                course.save(update_fields=list(course_defaults.keys()))
            else:
                course = Course.objects.create(**course_defaults)

            seeded_module_titles = [module_data["title"] for module_data in course_data["modules"]]
            Module.objects.filter(course=course).exclude(title__in=seeded_module_titles).delete()

            for module_index, module_data in enumerate(course_data["modules"], start=1):
                module, _ = Module.objects.update_or_create(
                    course=course,
                    title=module_data["title"],
                    defaults={"order": module_index},
                )

                seeded_lesson_titles = [lesson_data["title"] for lesson_data in module_data["lessons"]]
                Lesson.objects.filter(module=module).exclude(title__in=seeded_lesson_titles).delete()

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
                        quiz.questions.all().delete()
                        for question_index, question_data in enumerate(quiz_data["questions"], start=1):
                            question = QuizQuestion.objects.create(
                                quiz=quiz,
                                text=question_data["text"],
                                order=question_index,
                            )
                            for choice_index, (choice_text, is_correct) in enumerate(question_data["choices"], start=1):
                                QuizChoice.objects.create(
                                    question=question,
                                    text=choice_text,
                                    is_correct=is_correct,
                                    order=choice_index,
                                )

                    task_data = lesson_data.get("task")
                    if task_data:
                        Task.objects.filter(lesson=lesson).exclude(title=task_data["title"]).delete()
                        Task.objects.update_or_create(
                            lesson=lesson,
                            title=task_data["title"],
                            defaults={"instructions": task_data["instructions"]},
                        )

            self.stdout.write(self.style.SUCCESS(f"Seeded course {course_index}: {course.title}"))

        Course.objects.filter(title__in=["IELTS Essay Writing Master"]).exclude(
            id=Course.objects.get(title="IELTS Essay Writing Mastery").id
        ).delete()

        enrolled_course_titles = ["Everyday English Speaking", "Grammar Foundations"]
        for course_title in enrolled_course_titles:
            course = Course.objects.get(title=course_title)
            Enrollment.objects.get_or_create(student=student, course=course)
            EnrollmentRequest.objects.update_or_create(
                student=student,
                course=course,
                defaults={"status": EnrollmentRequest.Status.APPROVED},
            )

        starter_course = Course.objects.get(title="Everyday English Speaking")
        completed_lessons = [
            Lesson.objects.get(module__course=starter_course, title="Greetings and Introductions"),
            Lesson.objects.get(module__course=starter_course, title="Talking About Yourself"),
            Lesson.objects.get(module__course__title="Grammar Foundations", title="Present Simple"),
        ]
        for lesson in completed_lessons:
            ProgressRecord.objects.update_or_create(
                student=student,
                lesson=lesson,
                defaults={"is_completed": True},
            )

        first_lesson = completed_lessons[0]
        first_quiz = Quiz.objects.filter(lesson=first_lesson).prefetch_related("questions__choices").first()
        if first_quiz:
            selected_answers = {}
            score = 0
            questions = list(first_quiz.questions.all())
            for question in questions:
                correct_choice = question.choices.filter(is_correct=True).first()
                if correct_choice:
                    selected_answers[str(question.id)] = correct_choice.id
                    score += 1
            QuizSubmission.objects.filter(student=student, quiz=first_quiz).delete()
            QuizSubmission.objects.create(
                student=student,
                quiz=first_quiz,
                selected_answers=selected_answers,
                score=score,
                total_questions=len(questions),
            )

        first_task = Task.objects.filter(lesson=first_lesson).first()
        if first_task:
            TaskSubmission.objects.update_or_create(
                student=student,
                task=first_task,
                defaults={
                    "answer_text": "Hello! My name is Demo Student. I live in Almaty. I like learning English and practicing speaking.",
                    "status": TaskSubmission.Status.REVIEWED,
                    "score": 88,
                    "teacher_feedback": "Good introduction. Try to add one more detail about your hobby.",
                    "reviewed_at": timezone.now(),
                },
            )

        grammar_task = Task.objects.filter(
            lesson__module__course__title="Grammar Foundations",
            lesson__title="Present Simple",
        ).first()
        if grammar_task:
            TaskSubmission.objects.update_or_create(
                student=student,
                task=grammar_task,
                defaults={
                    "answer_text": "I wake up at seven. I study English every morning. I eat lunch at school. I watch videos in the evening.",
                    "status": TaskSubmission.Status.SUBMITTED,
                    "score": None,
                    "teacher_feedback": "",
                    "reviewed_at": None,
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
