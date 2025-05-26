from bson import ObjectId
from fastapi import HTTPException, status


def get_object_id(receive_id: str) -> ObjectId:
    """Получение ObjectId из переданной строки."""
    try:
        return ObjectId(receive_id)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ObjectId: {receive_id}"
        )


def get_string_id(object_id: ObjectId) -> str:
    """
    Преобразование ObjectId в его строковое представление.
    Если на вход передано невалидное значение, выбрасывает HTTPException 400.
    """
    if not isinstance(object_id, ObjectId):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid type for ObjectId: {object_id!r}"
        )
    try:
        return str(object_id)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error converting ObjectId to string: {exc}"
        )
