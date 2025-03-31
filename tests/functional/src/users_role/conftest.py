import pytest
import requests
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from settings import config
from utils import FixtureError
from testdata import UserCreateRequest, UserLoginRequest, UserRoleEnum


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
def create_superuser_data_request_f() -> UserCreateRequest:
    return (
        UserCreateRequest(
            first_name="first_name_superuser_test",
            last_name="last_name_superuser_test",
            login="login_superuser_test",
            password="password_superuser_test",
        )
    )


@pytest.fixture
def login_superuser_data_request_f() -> UserLoginRequest:
    return (
        UserLoginRequest(
            username="login_superuser_test",
            password="password_superuser_test",
        )
    )


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
def remove_superuser_db_f(pg_session, create_superuser_data_request_f: UserCreateRequest) -> None:
    """
    Fixture: удаление суперпользователя из DB.

    @type pg_session:
    @param pg_session:
    @type create_superuser_data_request_f: UserCreateRequest
    @param create_superuser_data_request_f:

    @rtype: None
    @return:
    """
    pg_session.execute(
        text(
            "DELETE FROM users WHERE login = :login AND "
            "EXISTS (SELECT 1 FROM users WHERE login = :login)"
        ),
        {
            "login": create_superuser_data_request_f.login,
        },
    )

    try:
        pg_session.commit()

    except SQLAlchemyError:
        pg_session.rollback()
        raise


@pytest.fixture
def set_superuser_role_db_f(pg_session, create_superuser_data_request_f: UserCreateRequest) -> None:
    """
    Fixture: пользователю присваивается роль "суперпользователя" DB.

    @type pg_session:
    @param pg_session:
    @type create_superuser_data_request_f: UserCreateRequest
    @param create_superuser_data_request_f:

    @rtype: None
    @return:
    """
    pg_session.execute(
        text(
            "UPDATE users "
            f"SET role = '{UserRoleEnum.SUPERUSER.name}' "
            f"WHERE login = '{create_superuser_data_request_f.login}'"
        )
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


@pytest.fixture
def create_superuser_f(create_superuser_data_request_f: UserCreateRequest) -> requests.Response:
    """
    Fixture: регистрация суперпользователя.

    @type create_superuser_data_request_f: UserCreateRequest
    @param create_superuser_data_request_f:

    @rtype: requests.Response
    @return:
    """
    url_ = f"{config.service_url}/api/v1/users/register"
    payload_ = create_superuser_data_request_f.model_dump()

    return requests.post(url=url_, json=payload_)


@pytest.fixture
def create_and_login_superuser_f(
    create_superuser_f,
    login_superuser_data_request_f: UserLoginRequest,
    request,
) -> requests.Response:
    """
    Fixture: регистрация и авторизация суперпользователя.

    @type login_superuser_data_request_f: UserLoginRequest
    @param login_superuser_data_request_f:
    @type create_superuser_f:
    @param create_superuser_f:
    @type request:
    @param request:

    @rtype: requests.Response
    @return:
    """
    if not create_superuser_f.status_code == requests.status_codes.codes.CREATED:
        raise FixtureError(f"User not created: {create_superuser_f.status_code}")
    request.getfixturevalue("set_superuser_role_db_f")

    url_ = f"{config.service_url}/api/v1/users/login"
    payload_ = login_superuser_data_request_f.model_dump()

    return requests.post(url=url_, data=payload_)
