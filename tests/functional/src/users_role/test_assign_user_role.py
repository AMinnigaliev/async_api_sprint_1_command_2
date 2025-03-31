import requests

from settings import config
from utils import FixtureError
from testdata import Token, AuthHeaders, UserResponse, UserRoleEnum


def test_assign_user_role(
    create_user_f: requests.Response,
    create_and_login_superuser_f: requests.Response,
    request,
) -> None:
    """
    Тест: назначение роли пользователю.

    @type create_user_f: requests.Response
    @param create_user_f:
    @type create_and_login_superuser_f: requests.Response
    @param create_and_login_superuser_f:
    @type request:
    @param request:

    @rtype: None
    @return:
    """
    try:
        if not create_user_f.status_code == requests.status_codes.codes.CREATED:
            raise FixtureError(f"User not created: {create_user_f.status_code}")

        if not create_and_login_superuser_f.status_code == requests.status_codes.codes.OK:
            raise FixtureError(f"Superuser not login: {create_and_login_superuser_f.status_code}")

        created_user_data = UserResponse(**create_user_f.json())
        superuser_token_data = Token(**create_and_login_superuser_f.json())

        url_ = f"{config.service_url}/api/v1/users_role/{created_user_data.id}/assign-role/{UserRoleEnum.ADMIN}"
        headers_ = AuthHeaders(Authorization=f"Bearer {superuser_token_data.access_token}").model_dump()

        response_ = requests.post(url=url_, headers=headers_)
        status_code = response_.status_code

        assert status_code == requests.status_codes.codes.OK

        updated_role_user_data = UserResponse(**response_.json())
        assert updated_role_user_data.id == created_user_data.id
        assert updated_role_user_data.role == UserRoleEnum.ADMIN
        assert created_user_data.role != updated_role_user_data.role

    finally:
        request.getfixturevalue("remove_user_db_f")
        request.getfixturevalue("remove_superuser_db_f")
        request.getfixturevalue("clear_redis")
