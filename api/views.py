from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import TaskSerializer
from .models import Task
from .helpers import is_title_special, is_valid_description
from rest_framework.permissions import IsAuthenticated


class CreateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TaskSerializer(data=request.data)

        # Additional Challenge 1: Check if request data contains all required fields.
        if not all(field in request.data for field in ['title', 'description', 'status']):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Challenge: Check if the title is special.
        if is_title_special(request.data.get('title', '')):
            return Response({'error': 'Special titles are not allowed'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            # Challenge: Validate description using helper function.
            if not is_valid_description(request.data.get('description', '')):
                return Response({'error': 'Description must be at least 20 characters'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Additional Challenge 2: Check for unique title and enforce case-insensitivity.
            existing_task_with_title = Task.objects.filter(title__iexact=request.data['title']).first()
            if existing_task_with_title:
                return Response({'error': 'A task with a similar title already exists'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Additional Challenge 3: Validate description length.
            if len(request.data['description']) < 10:
                return Response({'error': 'Description must be at least 10 characters'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Additional Challenge 4: Ensure that the status is valid.
            valid_status_choices = [choice[0] for choice in Task.status_choices]
            if request.data['status'] not in valid_status_choices:
                return Response({'error': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
