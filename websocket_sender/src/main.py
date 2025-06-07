import logging
import sentry_sdk
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from src.core.config import settings
from src.core.logger import configure_logging  # тот же файл, что и в других сервисах
from src.db.rabbit_client import RabbitClient
from src.services.auth_service import verify_jwt
from src.services.connection_manager import manager

configure_logging()
logger = logging.getLogger(__name__)
rabbit_client = RabbitClient()
sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=1.0)

app = FastAPI(
    title="WebSocket Sender",
    default_response_class=ORJSONResponse,
)

FastAPIInstrumentor.instrument_app(app)

@app.on_event("startup")
async def startup():
    await rabbit_client.start()
    logger.info("🚀 WebSocket-Sender запущен")

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str):
    user_id = verify_jwt(token)
    if not user_id:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await manager.connect(user_id, ws)
    try:
        while True:            # bi-directional канал: клиент может отправлять «ping» и т.п.
            _ = await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, ws)
