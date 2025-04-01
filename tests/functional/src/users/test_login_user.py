import requests

from settings import config
from utils import FixtureError
from testdata import Token, UserUpdateRequest, AuthHeaders, UserResponse


def test_update_user(
    create_and_login_user_f: requests.Response,
    update_user_data_request_f: UserUpdateRequest,
    request,
) -> None:
    """
    Тест: обновление данных пользователя.

    @type create_and_login_user_f: requests.Response
    @param create_and_login_user_f:
    @type update_user_data_request_f: UserUpdateRequest
    @param update_user_data_request_f:
    @type request:
    @param request:

    @rtype: None
    @return:
    """
    try:
        if not create_and_login_user_f.status_code == requests.status_codes.codes.OK:
            raise FixtureError(f"User not login: {create_and_login_user_f.status_code}")
        token_data = Token(**create_and_login_user_f.json())

        url_ = f"{config.service_url}/api/v1/users/update"
        payload_ = update_user_data_request_f.model_dump()
        headers_ = AuthHeaders(Authorization=f"Bearer {token_data.access_token}").model_dump()

        response_ = requests.patch(url=url_, json=payload_, headers=headers_)
        status_code = response_.status_code

        assert status_code == requests.status_codes.codes.OK

        updated_user_data = UserResponse(**response_.json())
        assert updated_user_data.first_name == update_user_data_request_f.first_name
        assert updated_user_data.last_name == update_user_data_request_f.last_name

    finally:
        request.getfixturevalue("remove_user_db_f")
        request.getfixturevalue("clear_redis")
