from django.urls import path
from .views import CreateTaskView

app_name = 'api'

urlpatterns = [
    path('tasks/', CreateTaskView.as_view(), name='create-task'),
]
