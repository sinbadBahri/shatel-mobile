import time
import pytest

from datetime import timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# Fixtures

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'username': 'testusername',
        'password': 'testpassword',
    }


@pytest.fixture
def authenticated_user(api_client, user_data):
    # Create a user
    user = User.objects.create_user(**user_data)

    # Obtain a token
    url = reverse('token_obtain_pair')
    data = {
        'username': user_data['username'],
        'password': user_data['password'],
    }
    response = api_client.post(url, data, format='json')

    # Check if the obtained access token can be used in subsequent requests
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    return api_client, user


@pytest.fixture
def access_token(authenticated_user):
    api_client, user = authenticated_user
    refresh = RefreshToken.for_user(user)
    return refresh.access_token


# Tests

@pytest.mark.django_db
def test_obtain_token(api_client, user_data):
    # Create a user
    User.objects.create_user(**user_data)

    # Endpoint for token obtain
    endpoint = '/api/token/'

    # Data for the request
    data = {
        'username': user_data['username'],
        'password': user_data['password'],
    }

    # Make a POST request to obtain token
    response = api_client.post(endpoint, data, format='json')

    # Ensure the request was successful
    assert response.status_code == status.HTTP_200_OK

    # Ensure the response contains access and refresh tokens
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_refresh_token(api_client, user_data):
    # Create a user
    user = User.objects.create_user(**user_data)

    # Obtain a refresh token
    refresh = RefreshToken.for_user(user)
    refresh_token = str(refresh)

    # URL for token refresh endpoint
    endpoint = '/api/token/refresh/'

    # Data for the request
    data = {
        'refresh': refresh_token,
    }

    # Make a POST request to refresh token
    response = api_client.post(endpoint, data, format='json')

    # Ensure the request was successful
    assert response.status_code == status.HTTP_200_OK

    # Ensure the response contains a new access token
    assert 'access' in response.data


@pytest.mark.django_db
def test_authenticated_create_task(authenticated_user):
    api_client, user = authenticated_user

    # URL for the create task view
    url = reverse('api:create-task')

    # Data for the request
    task_data = {
        'title': 'Task-1',
        'description': 'This is Task number 1.',
        'status': 'INPROGRESS',
    }

    # Make a POST request to create a task
    response = api_client.post(url, data=task_data, format='json')

    # Ensure the request was successful
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_unauthenticated_create_task(api_client):
    # URL for the create task view
    url = reverse('api:create-task')

    # Data for the request
    task_data = {
        'title': 'Task-2',
        'description': 'This is Task number 2.',
        'status': 'INPROGRESS',
    }

    # Make a POST request to create a task without authentication
    response = api_client.post(url, data=task_data, format='json')

    # Ensure the request was unsuccessful since it requires authentication
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_expired_access_token(api_client, access_token):
    # Override access token lifetime for this test
    access_token.set_exp(lifetime=timedelta(seconds=5))
    valid_access_token = str(access_token)

    # Access a protected view with a valid token
    url = reverse('api:create-task')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_access_token}')
    response = api_client.post(url,
                               data={
                                   'title': 'Task-2',
                                   'description': 'This is Task number 2.',
                                   'status': 'INPROGRESS',
                               }
                               )
    assert response.status_code == 201

    # Wait for the token to expire
    expiration_time = timedelta(seconds=5).total_seconds() + 1
    time.sleep(expiration_time)

    # Attempt to access the protected view with the expired token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_access_token}')
    response = api_client.post(url,
                               data={
                                   'title': 'Task-4',
                                   'description': 'This is Task number 4.',
                                   'status': 'INPROGRESS',
                               }
                               )

    # Ensure that request with an expired token is rejected
    assert response.status_code == 401


@pytest.mark.django_db
def test_tampered_token(api_client, access_token):
    url = reverse('api:create-task')

    # Generate a valid access token
    valid_access_token = str(access_token)

    # Attempt to access the protected view with a tampered token
    tampered_token = valid_access_token[:-1] + 'louy8w'
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tampered_token}')
    response = api_client.get(url)

    # Ensure that request with tampered token is rejected
    assert response.status_code == 401


@pytest.mark.django_db
def test_attempt_with_missing__token(api_client):
    url = reverse('api:create-task')

    # Attempt to access the protected view without providing Authentication credentials
    response = api_client.get(url)

    # Ensure the response has the appropriate error message
    assert response.status_code == 401
    assert response.data.get('detail') == ErrorDetail(string='Authentication credentials were not provided.',
                                                      code='not_authenticated')


@pytest.mark.django_db
def test_malformed_token_header_with_appropriate_error(api_client):
    url = reverse('api:create-task')

    # Attempt to access the protected view with an invalid token
    invalid_token = "invalid_token"
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {invalid_token}')
    response = api_client.get(url)

    # Ensure the status is Unauthorized
    assert response.status_code == 401

    # Ensure the response has the appropriate error message
    assert response.data.get('code') == ErrorDetail(string='token_not_valid', code='token_not_valid')


@pytest.mark.django_db
def test_can_not_obtain_access_token_from_expired_refresh_token(api_client, authenticated_user):
    api, user = authenticated_user
    # Generate an expired refresh token
    expired_refresh = RefreshToken.for_user(user)
    expired_refresh.set_exp(lifetime=timedelta(seconds=3))

    # Wait for the token to expire
    expiration_time = timedelta(seconds=3).total_seconds() + 1
    time.sleep(expiration_time)

    # Use the expired refresh token to create a new access token
    endpoint = '/api/token/refresh/'
    data = {'refresh': str(expired_refresh)}
    response = api_client.post(endpoint, data=data, format='json')

    # Ensure the status is Unauthorized
    assert response.status_code == 401

    # Ensure the response doesn't contain any access token
    assert 'access' not in response.data


@pytest.mark.django_db
def test_expired_refresh_token_with_correct_error(api_client, authenticated_user):
    api, user = authenticated_user
    # Generate an expired refresh token
    expired_refresh = RefreshToken.for_user(user)
    expired_refresh.set_exp(lifetime=timedelta(seconds=3))

    # Wait for the token to expire
    expiration_time = timedelta(seconds=3).total_seconds() + 1
    time.sleep(expiration_time)

    # Use the expired refresh token to create a new access token
    endpoint = '/api/token/refresh/'
    data = {'refresh': str(expired_refresh)}
    response = api_client.post(endpoint, data=data, format='json')

    # Ensure the response has the appropriate error message
    assert response.status_code == 401
    assert response.data.get('detail') == ErrorDetail(string='Token is invalid or expired',
                                                      code='token_not_valid')

