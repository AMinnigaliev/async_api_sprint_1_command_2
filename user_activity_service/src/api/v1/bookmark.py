from uuid import UUID

from fastapi import APIRouter, Depends

from src.dependencies.auth import (role_dependency,
                                   role_dependency_exp_important)
from src.dependencies.movies import film_existence_dependency
from src.schemas.bookmark import BookmarkResponse, DeleteBookmarkResponse
from src.schemas.user_role_enum import UserRoleEnum
from src.services.bookmark_service import BookmarkService, get_bookmark_service

router = APIRouter()


@router.post(
    "/{film_id}/create",
    summary="Добавить закладку на фильм",
    response_model=BookmarkResponse,
)
async def create_bookmark(
    film_id: UUID = Depends(film_existence_dependency),
    token_payload: dict = Depends(
        role_dependency_exp_important(UserRoleEnum.get_all_roles())
    ),
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
) -> BookmarkResponse:
    """Эндпоинт для добавления пользовательской закладки на фильм."""
    return await bookmark_service.create(film_id, token_payload)


@router.delete(
    "/{bookmark_id}/delete",
    summary="Удалить пользовательскую закладку на фильм",
    response_model=DeleteBookmarkResponse,
)
async def delete_bookmark(
    bookmark_id: UUID,
    token_payload: dict = Depends(
        role_dependency_exp_important(UserRoleEnum.get_all_roles())
    ),
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
) -> DeleteBookmarkResponse:
    """Эндпоинт для удаления пользовательской закладки на фильм."""
    await bookmark_service.delete(bookmark_id, token_payload)
    return DeleteBookmarkResponse(message="Bookmark deleted successfully")


@router.get(
    "",
    summary="Закладки пользователя",
    response_model=list[BookmarkResponse],
)
async def list_bookmark(
    token_payload: dict = Depends(role_dependency(UserRoleEnum.get_all_roles())),
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
) -> list[BookmarkResponse]:
    """Эндпоинт для получения списка закладок пользователя на фильмы"""
    return await bookmark_service.get_bookmarks(token_payload)
