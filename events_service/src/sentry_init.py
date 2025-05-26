import os
import sentry_sdk
from importlib import import_module

_framework = os.getenv("SENTRY_FRAMEWORK")  # fastapi / flask / django / plain

_integrations = {
    "django": "sentry_sdk.integrations.django:DjangoIntegration",
    "fastapi": "sentry_sdk.integrations.fastapi:FastApiIntegration",
    "flask": "sentry_sdk.integrations.flask:FlaskIntegration",
}.get(_framework)

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("SENTRY_ENV", "local"),
    integrations=[import_module(_integrations.split(":")[0]).__getattribute__(
        _integrations.split(":")[1]
    )()] if _integrations else [],
    traces_sample_rate=1.0,
)
