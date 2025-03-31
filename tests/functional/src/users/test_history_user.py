import requests

from settings import config
from utils import FixtureError
from testdata import Token, AuthHeaders, UserHistoryResponse


def test_history_user(
    create_and_login_user_f: requests.Response,
    request,
) -> None:
    """
    Тест: получение истории входа пользователя.

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
        token_data = Token(**create_and_login_user_f.json())

        url_ = f"{config.service_url}/api/v1/users/history"
        headers_ = AuthHeaders(Authorization=f"Bearer {token_data.access_token}").model_dump()

        response_ = requests.get(url=url_, headers=headers_)
        status_code = response_.status_code

        assert status_code == requests.status_codes.codes.OK

        user_login_history = [UserHistoryResponse(**res_lst) for res_lst in response_.json()]
        assert len(user_login_history) == 1

        user_first_login_history = next(iter(user_login_history))
        assert user_first_login_history.user_id is not None
        assert user_first_login_history.login_time is not None
        assert user_first_login_history.user_agent is not None

    finally:
        request.getfixturevalue("remove_user_db_f")
        request.getfixturevalue("clear_redis")
