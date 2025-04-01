import requests

from settings import config
from utils import FixtureError
from testdata import Token, RefreshToken


def test_refresh_token_user(
    create_and_login_user_f: requests.Response,
    request,
) -> None:
    """
    Тест: обновление refresh-токена.

    @type create_and_login_user_f: requests.Response
    @param create_and_login_user_f:
    @type request:
    @param request:

    @rtype: None
    @return:
    """
    try:
        if not create_and_login_user_f.status_code == requests.status_codes.codes.OK:
            raise FixtureError(f"User not login: {create_and_login_user_f.status_code}")
        old_token_data = Token(**create_and_login_user_f.json())

        url_ = f"{config.service_url}/api/v1/users/refresh"
        payload_ = RefreshToken(refresh_token=old_token_data.refresh_token).model_dump()

        response_ = requests.post(url=url_, params=payload_)
        status_code = response_.status_code

        assert status_code == requests.status_codes.codes.OK

        new_token_data = Token(**response_.json())
        assert new_token_data.access_token is not None
        assert new_token_data.refresh_token is not None
        assert new_token_data.access_token == old_token_data.access_token
        assert new_token_data.refresh_token == old_token_data.refresh_token

    finally:
        request.getfixturevalue("remove_user_db_f")
        request.getfixturevalue("clear_redis")
