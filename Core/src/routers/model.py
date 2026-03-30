import uuid
from typing import List

from fastapi import APIRouter, Depends, Query
from shared import ModelHandler, RequestModel
from shared_db import get_session
from shared_utils import AccessContext
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Models"], prefix="/model")


@router.get("/fetch/one", response_model=RequestModel)
async def get_model_details(
    model_id: uuid.UUID = Query(..., description="UUID del modelo a obtener"),
    ctx: AccessContext = Depends(),
    db: AsyncSession = Depends(get_session),
):
    return await ModelHandler(db=db).ModelRead(model_id)


@router.get("/fetch/all", response_model=List[RequestModel])
async def get_models(
    ctx: AccessContext = Depends(), db: AsyncSession = Depends(get_session)
):
    return await ModelHandler(db=db).ModelReadAll()
