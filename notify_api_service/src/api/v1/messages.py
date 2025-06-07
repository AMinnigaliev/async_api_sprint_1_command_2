from fastapi import APIRouter, Depends

from src.dependencies.request import get_request_id
from src.schemas.message import IncomingMessage
from src.services.messages_service import MessagesService, get_messages_service

router = APIRouter()


@router.post("")
async def accept_message(
    message: IncomingMessage,
    request_id: str = Depends(get_request_id),
    messages_service: MessagesService = Depends(get_messages_service),

):
    await messages_service.accept_message(request_id, message)
