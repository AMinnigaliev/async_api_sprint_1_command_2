import time

import requests
from requests.exceptions import RequestException
from logger import logger
from settings import config


def wait_for_service(url: str, timeout: int = 30):
    start_time = time.time()

    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logger.debug(f"Service is up and running at {url}")
                break

        except RequestException as ex:
            logger.error(f"RequestException({url}): {ex}")

        if (time.time() - start_time) > timeout:
            raise TimeoutError(f"Service at {url} did not become available within {timeout} seconds")

        time.sleep(1)


if __name__ == "__main__":
    health_check_url = f"http://{config.src_app_host}:{config.src_app_port}/api/v1"
    wait_for_service(url=health_check_url)
