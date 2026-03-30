import uuid
from typing import List

from fastapi import APIRouter, Depends, Form, Query
from shared import (
    PromptHandler,
    RequestPrompt,
    ResponsePrompt,
    validate_prompt,
)
from shared_db import get_session
from shared_schemas import ResponseMessage
from shared_utils import AccessContext, get_claims
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Prompts"], prefix="/prompt")


@router.post("/new", response_model=ResponsePrompt)
async def upload_media(
    prompt: RequestPrompt = Depends(validate_prompt),
    ctx: AccessContext = Depends(),
    db: AsyncSession = Depends(get_session),
):
    claims = get_claims(ctx.access_token)
    current_user = claims["sub"]
    return await PromptHandler(db=db, current_user=current_user).PromptCreate(
        prompt.prompt_text
    )


@router.get("/fetch/one", response_model=ResponsePrompt)
async def get_media(
    prompt_id: uuid.UUID = Query(..., description="UUID del prompt a obtener"),
    ctx: AccessContext = Depends(),
    db: AsyncSession = Depends(get_session),
):
    claims = get_claims(ctx.access_token)
    current_user = claims["sub"]
    return await PromptHandler(db=db, current_user=current_user).PromptRead(prompt_id)


@router.get("/fetch/all", response_model=List[ResponsePrompt])
async def get_all_media(
    ctx: AccessContext = Depends(), db: AsyncSession = Depends(get_session)
):
    claims = get_claims(ctx.access_token)
    current_user = claims["sub"]
    return await PromptHandler(db=db, current_user=current_user).PromptReadAll()


@router.put("/update/", response_model=ResponsePrompt)
async def replace_media(
    prompt_id: uuid.UUID = Form(..., description="UUID del prompt a modificar"),
    prompt_text: str = Form(..., description="Nueva tarea a realizar"),
    ctx: AccessContext = Depends(),
    db: AsyncSession = Depends(get_session),
):
    claims = get_claims(ctx.access_token)
    current_user = claims["sub"]
    return await PromptHandler(db=db, current_user=current_user).PromptUpdate(
        prompt_id, prompt_text
    )


@router.delete("/delete/", response_model=ResponseMessage)
async def delete_media(
    prompt_id: uuid.UUID = Form(..., description="UUID del prompt a eliminar"),
    ctx: AccessContext = Depends(),
    db: AsyncSession = Depends(get_session),
):
    claims = get_claims(ctx.access_token)
    current_user = claims["sub"]
    return await PromptHandler(db=db, current_user=current_user).PromptDelete(prompt_id)
