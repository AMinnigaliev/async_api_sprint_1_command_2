import requests

from settings import config
from testdata import UserCreateRequest, UserResponse


def test_register_user(create_user_data_request_f: UserCreateRequest, request) -> None:
    """
    Тест: регистрация пользователя.

    @type create_user_data_request_f: UserCreateRequest
    @param create_user_data_request_f:
    @type request:
    @param request:

    @rtype: None
    @return:
    """
    try:
        url_ = f"{config.service_url}/api/v1/users/register"
        payload_ = create_user_data_request_f.model_dump()

        response_ = requests.post(url=url_, json=payload_)
        status_code = response_.status_code

        assert status_code == requests.status_codes.codes.CREATED, f"Users not register: {status_code}"

        created_user_data = UserResponse(**response_.json())
        assert created_user_data.id is not None
        assert created_user_data.first_name == create_user_data_request_f.first_name
        assert created_user_data.last_name == create_user_data_request_f.last_name
        assert created_user_data.role is not None

    finally:
        request.getfixturevalue("remove_user_db_f")
