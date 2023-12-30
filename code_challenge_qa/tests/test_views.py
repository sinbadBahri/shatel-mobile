import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


# Fixtures

@pytest.fixture
def user():
    return User.objects.create_user({
        'username': 'testusername',
        'password': 'testpassword',
    })


@pytest.fixture
def valid_token(user):
    return AccessToken.for_user(user)


@pytest.fixture
def api_client(valid_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_token}')
    return client


# Tests

@pytest.mark.django_db
@pytest.mark.parametrize('data, expected_error', [
    ({'title': 'Title', 'description': 'This is a ValidDescription', 'status': 'TODO'}, None),
    ({'title': '$Title', 'description': 'This is a ValidDescription', 'status': 'TODO'}, 'Special titles are not allowed'),
    ({'title': 'Title', 'description': 'ShortDesc', 'status': 'TODO'}, 'Description must be at least 20 characters'),
    ({'title': 'Title', 'description': 'This is a ValidDescription'}, 'Missing required fields'),
    ({'description': 'This is a ValidDescription', 'status': 'TODO'}, 'Missing required fields'),
    ({'title': 'Title', 'status': 'TODO'}, 'Missing required fields'),
    ({}, 'Missing required fields'),
])
def test_create_task_error_handling(api_client, data, expected_error):
    # Attempt to create a new task with parametrized data
    response = api_client.post('/tasks/', data=data, format='json')

    # Check if the status is Bad Request with the correct error
    if expected_error:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get('error') == expected_error
    else:
        # Ensure the status is Created when correct data has been given
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_task_with_duplicate_title_error_handling(api_client):
    # Create a task with a specific title in the database
    task_data = {
        'title': "TestTitle",
        'description': "This is a Description for Testing",
        'status': 'TODO'
    }
    api_client.post('/tasks/', data=task_data, format='json')

    # Attempt to create a new task with the same title
    new_task_data = {
        'title': "TestTitle",
        'description': "This is a total NewDescription for Testing",
        'status': 'INPROGRESS'
    }
    response = api_client.post('/tasks/', data=new_task_data, format='json')

    # Ensure the status is Bad Request
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Check that the response has the appropriate error message
    assert response.data.get('error') == 'A task with a similar title already exists'
