import requests

from settings import config
from utils import FixtureError
from testdata import Token, AuthHeaders, UserLogoutRequest, UserLogoutResponse


def test_logout_user(
    create_and_login_user_f: requests.Response,
    user_logout_data_response_f: UserLogoutResponse,
    request,
) -> None:
    """
    Тест: выход пользователя из системы.

    @type create_and_login_user_f: requests.Response
    @param create_and_login_user_f:
    @type user_logout_data_response_f: UserLogoutResponse
    @param user_logout_data_response_f:
    @type request:
    @param request:

    @rtype: None
    @return:
    """
    try:
        if not create_and_login_user_f.status_code == requests.status_codes.codes.OK:
            raise FixtureError(f"User not login: {create_and_login_user_f.status_code}")
        token_data = Token(**create_and_login_user_f.json())

        url_ = f"{config.service_url}/api/v1/users/logout"
        payload_ = UserLogoutRequest(refresh_token=token_data.refresh_token).model_dump()
        headers_ = AuthHeaders(Authorization=f"Bearer {token_data.access_token}").model_dump()

        response_ = requests.post(url=url_, params=payload_, headers=headers_)
        status_code = response_.status_code

        assert status_code == requests.status_codes.codes.OK

        user_logout_data = UserLogoutResponse(**response_.json())
        assert user_logout_data.message == user_logout_data_response_f.message

    finally:
        request.getfixturevalue("remove_user_db_f")
        request.getfixturevalue("clear_redis")
