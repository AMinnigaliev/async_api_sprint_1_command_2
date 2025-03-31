import pytest
import requests
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from settings import config
from utils import FixtureError
from testdata import UserCreateRequest, UserLoginRequest, UserUpdateRequest, UserLogoutResponse


@pytest.fixture
def create_user_data_request_f() -> UserCreateRequest:
    return (
        UserCreateRequest(
            first_name="first_name_test",
            last_name="last_name_test",
            login="login_test",
            password="password_test",
        )
    )


@pytest.fixture
def login_user_data_request_f() -> UserLoginRequest:
    return (
        UserLoginRequest(
            username="login_test",
            password="password_test",
        )
    )


@pytest.fixture
def update_user_data_request_f() -> UserUpdateRequest:
    return (
        UserUpdateRequest(
            first_name="first_name_test",
            last_name="last_name_update_test",
            password="password_test",
        )
    )


@pytest.fixture
def user_logout_data_response_f() -> UserLogoutResponse:
    return UserLogoutResponse(message="Successfully logged out")


@pytest.fixture
def remove_user_db_f(pg_session, create_user_data_request_f: UserCreateRequest) -> None:
    """
    Fixture: удаление пользователя из DB.

    @type pg_session:
    @param pg_session:
    @type create_user_data_request_f: UserCreateRequest
    @param create_user_data_request_f:

    @rtype: None
    @return:
    """
    pg_session.execute(
        text(
            "DELETE FROM users WHERE login = :login AND "
            "EXISTS (SELECT 1 FROM users WHERE login = :login)"
        ),
        {
            "login": create_user_data_request_f.login,
        },
    )

    try:
        pg_session.commit()

    except SQLAlchemyError:
        pg_session.rollback()
        raise


@pytest.fixture
def create_user_f(create_user_data_request_f: UserCreateRequest) -> requests.Response:
    """
    Fixture: регистрация пользователя.

    @type create_user_data_request_f: UserCreateRequest
    @param create_user_data_request_f:

    @rtype: requests.Response
    @return:
    """
    url_ = f"{config.service_url}/api/v1/users/register"
    payload_ = create_user_data_request_f.model_dump()

    return requests.post(url=url_, json=payload_)


@pytest.fixture
def create_and_login_user_f(create_user_f, login_user_data_request_f: UserLoginRequest) -> requests.Response:
    """
    Fixture: регистрация и авторизация пользователя.

    @type create_user_f:
    @param create_user_f:
    @type login_user_data_request_f: UserLoginRequest
    @param login_user_data_request_f:

    @rtype: requests.Response
    @return:
    """
    if not create_user_f.status_code == requests.status_codes.codes.CREATED:
        raise FixtureError(f"User not created: {create_user_f.status_code}")

    url_ = f"{config.service_url}/api/v1/users/login"
    payload_ = login_user_data_request_f.model_dump()

    return requests.post(url=url_, data=payload_)
