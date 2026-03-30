import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, Form, Query, UploadFile
from fastapi.responses import FileResponse
from models import MediaType
from shared import MediaHandler, MediaUtils, ResponseMedia
from shared_db import get_session
from shared_schemas import ResponseMessage
from shared_utils import AccessContext, get_claims
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Archivos"], prefix="/media")

BASE_UPLOAD_DIR = os.getenv("BASE_UPLOAD_DIR", "/app/uploads")

os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)


@router.get("/fetch/one", response_class=FileResponse)
async def get_media(
    media_id: uuid.UUID = Query(..., description="UUID del media a obtener"),
    ctx: AccessContext = Depends(),
    db: AsyncSession = Depends(get_session),
):
    claims = get_claims(ctx.access_token)
    current_user = claims["sub"]
    return await MediaHandler(
        db=db, upload_dir=BASE_UPLOAD_DIR, current_user=current_user
    ).FileRead(media_id)


@router.get("/fetch/all", response_model=List[ResponseMedia])
async def get_all_media(
    ctx: AccessContext = Depends(),
    db: AsyncSession = Depends(get_session),
):
    claims = get_claims(ctx.access_token)
    current_user = claims["sub"]
    return await MediaHandler(
        db=db, upload_dir=BASE_UPLOAD_DIR, current_user=current_user
    ).FileReadAll()


@router.post("/upload/tabular", response_model=ResponseMedia)
async def upload_tabular(
    file: UploadFile = Depends(
        MediaUtils().validate_file(
            allowed_types=[
                MediaType.TABLE_EXCEL,
                MediaType.TABLE_OPEN,
                MediaType.TABLE_CSV,
                MediaType.TABLE_TSV,
            ]
        )
    ),
    ctx: AccessContext = Depends(),
    db: AsyncSession = Depends(get_session),
):
    claims = get_claims(ctx.access_token)
    current_user = claims["sub"]
    return await MediaHandler(
        db=db, upload_dir=BASE_UPLOAD_DIR, current_user=current_user
    ).FileCreate(file)


@router.post("/upload/media", response_model=ResponseMedia)
async def upload_media(
    file: UploadFile = Depends(
        MediaUtils().validate_file(
            allowed_types=[
                MediaType.IMAGE_PNG,
                MediaType.IMAGE_JPEG,
                MediaType.VIDEO_MP4,
            ]
        )
    ),
    ctx: AccessContext = Depends(),
    db: AsyncSession = Depends(get_session),
):
    claims = get_claims(ctx.access_token)
    current_user = claims["sub"]
    return await MediaHandler(
        db=db, upload_dir=BASE_UPLOAD_DIR, current_user=current_user
    ).FileCreate(file)


@router.put("/edit", response_model=ResponseMedia)
async def edit_media(
    media_id: uuid.UUID = Form(..., description="UUID del media a editar"),
    filename: str = Form(..., description="Nuevo nombre"),
    ctx: AccessContext = Depends(),
    db: AsyncSession = Depends(get_session),
):
    claims = get_claims(ctx.access_token)
    current_user = claims["sub"]
    return await MediaHandler(
        db=db, upload_dir=BASE_UPLOAD_DIR, current_user=current_user
    ).FileRename(id=media_id, new_filename=filename)


@router.delete("/delete/", response_model=ResponseMessage)
async def delete_media(
    media_id: uuid.UUID = Form(..., description="UUID del media a eliminar"),
    ctx: AccessContext = Depends(),
    db: AsyncSession = Depends(get_session),
):
    claims = get_claims(ctx.access_token)
    current_user = claims["sub"]
    return await MediaHandler(
        db=db, upload_dir=BASE_UPLOAD_DIR, current_user=current_user
    ).FileDelete(media_id)
