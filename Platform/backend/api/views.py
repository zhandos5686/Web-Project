from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Category, Course, Task, Enrollment, Profile, Submission
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    TaskSerializer,
    EnrollmentSerializer,
    ProfileSerializer,
    EnrollSerializer,
    SubmissionSerializer,
)


@api_view(['GET', 'POST'])
def category_list(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def course_list(request):
    if request.method == 'GET':
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def course_detail(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=course.created_by)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskListAPIView(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailAPIView(APIView):
    def get_object(self, task_id):
        try:
            return Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return None

    def get(self, request, task_id):
        task = self.get_object(task_id)
        if task is None:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, task_id):
        task = self.get_object(task_id)
        if task is None:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=task.created_by)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        task = self.get_object(task_id)
        if task is None:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EnrollmentListAPIView(APIView):
    def get(self, request):
        enrollments = Enrollment.objects.all()
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = EnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnrollmentDetailAPIView(APIView):
    def get_object(self, enrollment_id):
        try:
            return Enrollment.objects.get(pk=enrollment_id)
        except Enrollment.DoesNotExist:
            return None

    def get(self, request, enrollment_id):
        enrollment = self.get_object(enrollment_id)
        if enrollment is None:
            return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data)

    def put(self, request, enrollment_id):
        enrollment = self.get_object(enrollment_id)
        if enrollment is None:
            return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnrollmentSerializer(enrollment, data=request.data)
        if serializer.is_valid():
            serializer.save(user=enrollment.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, enrollment_id):
        enrollment = self.get_object(enrollment_id)
        if enrollment is None:
            return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)

        enrollment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={
                'full_name': request.user.username,
                'phone': '',
                'grade_level': '',
                'bio': '',
            }
        )
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={
                'full_name': request.user.username,
                'phone': '',
                'grade_level': '',
                'bio': '',
            }
        )
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyCoursesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
        courses = [enrollment.course for enrollment in enrollments]
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class MyTasksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
        course_ids = [enrollment.course.id for enrollment in enrollments]
        tasks = Task.objects.filter(course_id__in=course_ids)

        completed_task_ids = Submission.objects.filter(user=request.user).values_list('task_id', flat=True)

        result = []
        for task in tasks:
            task_data = TaskSerializer(task).data
            task_data['is_completed'] = task.id in completed_task_ids
            result.append(task_data)

        return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_in_course(request):
    serializer = EnrollSerializer(data=request.data)
    if serializer.is_valid():
        course_id = serializer.validated_data['course_id']

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'status': 'active'}
        )

        if not created:
            return Response({'message': 'Already enrolled'}, status=status.HTTP_200_OK)

        return Response(
            {
                'message': 'Enrolled successfully',
                'enrollment_id': enrollment.id
            },
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_task(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    submission, created = Submission.objects.get_or_create(
        user=request.user,
        task=task,
        defaults={
            'is_completed': True,
            'submitted_at': timezone.now()
        }
    )

    if not created:
        if not submission.is_completed:
            submission.is_completed = True
            submission.submitted_at = timezone.now()
            submission.save()

        return Response({'message': 'Task already completed'}, status=status.HTTP_200_OK)

    serializer = SubmissionSerializer(submission)
    return Response(
        {
            'message': 'Task marked as completed',
            'submission': serializer.data
        },
        status=status.HTTP_201_CREATED
    )