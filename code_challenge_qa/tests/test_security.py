import jwt
import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken


# Fixtures

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return get_user_model().objects.create_user(
        username='fuad',
        password='Fuad7777',
        email='fuad.kj@gmail.com'
    )


@pytest.fixture
def access_token(user):
    refresh = RefreshToken.for_user(user)
    return refresh.access_token


# Test

@pytest.mark.django_db
def test_validate_token_structure(access_token, user):
    token = str(access_token)

    # Ensure the token is a valid JWT
    decoded_token = jwt.decode(token, options={'verify_signature': False})

    # Ensure the token is an UntypedToken
    assert isinstance(UntypedToken(token), UntypedToken)

    # Ensure the token does not contain unintended data
    assert user.password not in decoded_token
    assert user.username not in decoded_token
    assert user.email not in decoded_token
